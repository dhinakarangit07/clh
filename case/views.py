from rest_framework import serializers
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from .models import Case
from client.models import Client
from advocate.models import Advocate
from django.contrib.auth.models import User
from .utils import solve_captcha_and_search

# Custom permission for advocates group
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='advocates').exists()

# Custom permission for client group
class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='client').exists()

# Custom permission for junior group
class IsJunior(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='junior').exists()

class CaseSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        help_text="Select the client for this case"
    )
    advocate = serializers.PrimaryKeyRelatedField(
        queryset=Advocate.objects.all(),
        required=False,
        allow_null=True,
        help_text="Select the advocate for this case (optional)"
    )
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    client_name = serializers.CharField(source='client.name', read_only=True)
    advocate_name = serializers.CharField(source='advocate.name', read_only=True, allow_null=True)

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'client', 'client_name', 'advocate', 'advocate_name', 'type', 'court', 'case_number',
            'cnr_number', 'file_no', 'file_name', 'reference_no', 'year', 'fir_no',
            'first_party', 'under_section', 'opposite_party', 'stage_of_case',
            'judge_name', 'next_hearing', 'status', 'priority', 'last_update',
            'description', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'last_update', 'created_at', 'created_by', 'client_name', 'advocate_name']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

class ClientCaseSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    advocate_name = serializers.CharField(source='advocate.name', read_only=True, allow_null=True)

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'client_name', 'advocate_name', 'type', 'court', 'case_number',
            'cnr_number', 'file_no', 'file_name', 'reference_no', 'year', 'fir_no',
            'first_party', 'under_section', 'opposite_party', 'stage_of_case',
            'judge_name', 'next_hearing', 'status', 'priority', 'last_update',
            'description', 'created_at'
        ]
        read_only_fields = fields  # All fields are read-only for clients

class JuniorCaseSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    advocate_name = serializers.CharField(source='advocate.name', read_only=True, allow_null=True)

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'client_name', 'advocate_name', 'type', 'court', 'case_number',
            'cnr_number', 'file_no', 'file_name', 'reference_no', 'year', 'fir_no',
            'first_party', 'under_section', 'opposite_party', 'stage_of_case',
            'judge_name', 'next_hearing', 'status', 'priority', 'last_update',
            'description', 'created_at'
        ]
        read_only_fields = fields  # All fields are read-only for junior advocates

class CaseListCreateView(generics.ListCreateAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Case.objects.filter(created_by=self.request.user)

class CaseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Case.objects.filter(created_by=self.request.user)

class CaseScrapeView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request, cnr_number):
        if not cnr_number:
            return Response(
                {"error": "CNR number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            scraped_data = solve_captcha_and_search(cnr_number)
            return Response(scraped_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to scrape data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ClientCaseListView(generics.ListAPIView):
    serializer_class = ClientCaseSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        # Get the Client instance associated with the logged-in user
        try:
            client = Client.objects.get(user=self.request.user)
            return Case.objects.filter(client=client)
        except Client.DoesNotExist:
            return Case.objects.none()

class ClientCaseDetailView(generics.RetrieveAPIView):
    serializer_class = ClientCaseSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        # Get the Client instance associated with the logged-in user
        try:
            client = Client.objects.get(user=self.request.user)
            return Case.objects.filter(client=client)
        except Client.DoesNotExist:
            return Case.objects.none()

class JuniorCaseListView(generics.ListAPIView):
    serializer_class = JuniorCaseSerializer
    permission_classes = [IsAuthenticated, IsJunior]

    def get_queryset(self):
        try:
            # Get the Advocate instance associated with the logged-in user
            advocate = Advocate.objects.get(user=self.request.user)
            # Check permissions
            if advocate.can_view_all_cases:
                return Case.objects.all()
            elif advocate.can_view_assigned_cases:
                return Case.objects.filter(advocate=advocate)
            else:
                return Case.objects.none()
        except Advocate.DoesNotExist:
            return Case.objects.none()

class JuniorCaseDetailView(generics.RetrieveAPIView):
    serializer_class = JuniorCaseSerializer
    permission_classes = [IsAuthenticated, IsJunior]

    def get_queryset(self):
        try:
            # Get the Advocate instance associated with the logged-in user
            advocate = Advocate.objects.get(user=self.request.user)
            # Check permissions
            if advocate.can_view_all_cases:
                return Case.objects.all()
            elif advocate.can_view_assigned_cases:
                return Case.objects.filter(advocate=advocate)
            else:
                return Case.objects.none()
        except Advocate.DoesNotExist:
            return Case.objects.none()