from rest_framework import serializers
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from .models import Reminder
from client.models import Client
from case.models import Case
from django.contrib.auth.models import User

# Custom permission for advocates group
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='advocates').exists()

# Custom permission for client group
class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='client').exists()

class ReminderSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        help_text="Select the client for this reminder"
    )
    case = serializers.PrimaryKeyRelatedField(
        queryset=Case.objects.all(),
        help_text="Select the case for this reminder"
    )
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    client_name = serializers.CharField(source='client.name', read_only=True)
    case_title = serializers.CharField(source='case.title', read_only=True)

    class Meta:
        model = Reminder
        fields = [
            'id', 'client', 'client_name', 'case', 'case_title', 'description',
            'date', 'time', 'frequency', 'emails', 'whatsapp', 'status',
            'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        """
        Ensure the case belongs to the selected client.
        """
        client = data.get('client')
        case = data.get('case')
        if client and case and case.client != client:
            raise serializers.ValidationError("The selected case does not belong to the selected client.")
        return data

class ClientReminderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    case_title = serializers.CharField(source='case.title', read_only=True)

    class Meta:
        model = Reminder
        fields = [
            'id', 'client_name', 'case_title', 'description',
            'date', 'time', 'frequency', 'emails', 'whatsapp', 'status',
            'created_at'
        ]
        read_only_fields = fields  # All fields are read-only for clients

class ReminderListCreateView(generics.ListCreateAPIView):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Reminder.objects.filter(created_by=self.request.user)

class ReminderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Reminder.objects.filter(created_by=self.request.user)

class ClientReminderListView(generics.ListAPIView):
    serializer_class = ClientReminderSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        try:
            client = Client.objects.get(user=self.request.user)
            return Reminder.objects.filter(case__client=client)
        except Client.DoesNotExist:
            return Reminder.objects.none()