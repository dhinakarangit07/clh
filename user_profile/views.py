
from django.shortcuts import render
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from client.views import Client
from senior_advocate.views import AdvocateRegistration
from student.views import LawStudent
from .models import Profile
from wagtail.images.models import Image

# Serializers for related models
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'email', 'contact_number', 'address', 'is_corporate', 'payment_amount', 'created_at']

class AdvocateRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocateRegistration
        fields = [
            'fathers_name', 'mothers_name', 'spouse_name', 'bar_council_name',
            'enrollment_roll_no', 'enrollment_date', 'place_of_practice',
            'area_of_practice', 'date_of_birth', 'communication_address',
            'contact_number', 'created_at'
        ]

class LawStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawStudent
        fields = [
            'name', 'email', 'mobile_no', 'fathers_name', 'mothers_name',
            'spouse_name', 'institution_name', 'course_type', 'roll_number',
            'study_year', 'dob', 'address', 'created_at'
        ]

class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    photo = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    client_details = serializers.SerializerMethodField()
    advocate_details = serializers.SerializerMethodField()
    student_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'photo', 'groups', 'client_details', 'advocate_details', 'student_details']

    def get_photo(self, obj):
        if hasattr(obj, 'profile') and obj.profile.photo:
            request = self.context.get('request')
            if request:
                # Build the full URL using the request's scheme and host
                return request.build_absolute_uri(obj.profile.photo.get_rendition('max-200x200').url)
            # Fallback to relative URL if request is not available
            return obj.profile.photo.get_rendition('max-200x200').url
        return None

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    def get_client_details(self, obj):
        if obj.groups.filter(name='client').exists():
            clients = Client.objects.filter(user=obj)
            return ClientSerializer(clients, many=True).data
        return []

    def get_advocate_details(self, obj):
        if obj.groups.filter(name='advocates').exists():
            advocates = AdvocateRegistration.objects.filter(created_by=obj)
            return AdvocateRegistrationSerializer(advocates, many=True).data
        return []

    def get_student_details(self, obj):
        if obj.groups.filter(name='students').exists():
            students = LawStudent.objects.filter(created_by=obj)
            return LawStudentSerializer(students, many=True).data
        return []

    def update(self, instance, validated_data):
        # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update Profile photo
        photo_file = self.context['request'].FILES.get('photo')
        if photo_file:
            try:
                profile = instance.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=instance)
            image = Image.objects.create(
                file=photo_file,
                title=f"{instance.username}_profile_photo",
                uploaded_by_user=instance
            )
            profile.photo = image
            profile.save()

        return instance

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords must match."})
        user = self.context['request'].user
        if not user.check_password(data['current_password']):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        serializer = ProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
