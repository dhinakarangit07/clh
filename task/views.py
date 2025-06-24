from rest_framework import serializers, status, generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from .models import Task, UploadedFile
from client.models import Client
from advocate.models import Advocate
from django.contrib.auth.models import User, Group
from django.db import models
from rest_framework.serializers import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Custom permission for advocates group or corporate clients
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user is in 'advocates' group
        is_advocate = request.user.groups.filter(name='advocates').exists()
        
        # Check if user is in 'client' group and has is_corporate=True
        is_corporate_client = False
        if request.user.groups.filter(name='client').exists():
            try:
                client = Client.objects.get(user=request.user)
                is_corporate_client = client.is_corporate
            except Client.DoesNotExist:
                pass
        
        return is_advocate or is_corporate_client

# Custom permission for junior group
class IsJunior(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='junior').exists()

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'name', 'file', 'size', 'type', 'uploaded_at', 'created_by']
        read_only_fields = ['id', 'uploaded_at', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    uploaded_files = UploadedFileSerializer(many=True, required=False)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    assigned_junior_advocate = serializers.PrimaryKeyRelatedField(
        queryset=Advocate.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'document_type', 'start_date', 'review_date',
            'deadline', 'priority', 'status', 'review_feedback', 'nda_details',
            'uploaded_files', 'created_at', 'updated_at', 'created_by', 'assigned_to',
            'assigned_junior_advocate'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def validate(self, data):
        start_date = data.get('start_date')
        deadline = data.get('deadline')
        if start_date and deadline and deadline < start_date:
            raise ValidationError({"deadline": "Deadline must be after start date."})

        review_date = data.get('review_date')
        if review_date and start_date and review_date < start_date:
            raise ValidationError({"review_date": "Review date must be after start date."})
        if review_date and deadline and review_date > deadline:
            raise ValidationError({"review_date": "Review date must be before deadline."})

        # Validate assigned_junior_advocate is in the junior group
        assigned_junior = data.get('assigned_junior_advocate')
        if assigned_junior and not assigned_junior.user.groups.filter(name='junior').exists():
            raise ValidationError({"assigned_junior_advocate": "Assigned junior advocate must be in the 'junior' group."})

        return data

    def create(self, validated_data):
        uploaded_files_data = validated_data.pop('uploaded_files', [])
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            try:
                client = Client.objects.get(user=request.user)
                if client.created_by:
                    validated_data['assigned_to'] = client.created_by
            except Client.DoesNotExist:
                validated_data['assigned_to'] = None

        task = Task.objects.create(**validated_data)

        for file_data in uploaded_files_data:
            UploadedFile.objects.create(task=task, **file_data)

        return task

    def update(self, instance, validated_data):
        uploaded_files_data = validated_data.pop('uploaded_files', [])
        request = self.context.get('request')

        # Only update assigned_to or assigned_junior_advocate if explicitly provided
        if 'assigned_to' not in validated_data and request and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                client = Client.objects.get(user=request.user)
                if client.created_by and instance.assigned_to is None:
                    validated_data['assigned_to'] = client.created_by
            except Client.DoesNotExist:
                pass

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if uploaded_files_data:
            instance.uploaded_files.all().delete()
            for file_data in uploaded_files_data:
                UploadedFile.objects.create(task=instance, **file_data)

        return instance

class JuniorTaskSerializer(serializers.ModelSerializer):
    uploaded_files = UploadedFileSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_junior_advocate_name = serializers.CharField(source='assigned_junior_advocate.name', read_only=True, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'document_type', 'start_date', 'review_date',
            'deadline', 'priority', 'status', 'review_feedback', 'nda_details',
            'uploaded_files', 'created_at', 'updated_at', 'created_by', 'created_by_name',
            'assigned_junior_advocate', 'assigned_junior_advocate_name'
        ]
        read_only_fields = fields  # All fields are read-only for junior advocates

@method_decorator(csrf_exempt, name='dispatch')
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Task.objects.filter(
            models.Q(created_by=self.request.user) | models.Q(assigned_to=self.request.user)
        ).distinct()

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        uploaded_files_data = []
        for file in files:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                return Response({"detail": f"File {file.name} exceeds 10MB limit."}, status=status.HTTP_400_BAD_REQUEST)
            uploaded_files_data.append({
                'name': file.name,
                'size': file.size,
                'type': file.content_type,
                'file': file,
                'created_by': request.user
            })

        serializer.validated_data['uploaded_files'] = uploaded_files_data
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

@method_decorator(csrf_exempt, name='dispatch')
class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Task.objects.filter(
            models.Q(created_by=self.request.user) | models.Q(assigned_to=self.request.user)
        ).distinct()

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        files = request.FILES.getlist('files')
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)

        uploaded_files_data = []
        for file in files:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                return Response({"detail": f"File {file.name} exceeds 10MB limit."}, status=status.HTTP_400_BAD_REQUEST)
            uploaded_files_data.append({
                'name': file.name,
                'size': file.size,
                'type': file.content_type,
                'file': file,
                'created_by': request.user
            })

        serializer.validated_data['uploaded_files'] = uploaded_files_data
        self.perform_update(serializer)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class AssignedTaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user).distinct()

@method_decorator(csrf_exempt, name='dispatch')
class JuniorTaskListView(generics.ListAPIView):
    serializer_class = JuniorTaskSerializer
    permission_classes = [IsAuthenticated, IsJunior]

    def get_queryset(self):
        try:
            advocate = Advocate.objects.get(user=self.request.user)
            return Task.objects.filter(assigned_junior_advocate=advocate).distinct()
        except Advocate.DoesNotExist:
            return Task.objects.none()

@method_decorator(csrf_exempt, name='dispatch')
class JuniorTaskStatusUpdateView(generics.UpdateAPIView):
    serializer_class = JuniorTaskSerializer
    permission_classes = [IsAuthenticated, IsJunior]

    def get_queryset(self):
        try:
            advocate = Advocate.objects.get(user=self.request.user)
            return Task.objects.filter(assigned_junior_advocate=advocate)
        except Advocate.DoesNotExist:
            return Task.objects.none()

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        data = {'status': request.data.get('status')}
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Restrict status changes to allowed values
        allowed_statuses = ['in_review', 'feedback_required', 'completed']
        if data['status'] not in allowed_statuses:
            return Response(
                {"detail": f"Junior advocates can only set status to {', '.join(allowed_statuses)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_update(serializer)
        return Response(serializer.data)