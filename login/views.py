import json
import requests
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, CharField, ValidationError, FileField, DateField
from django.contrib.auth.models import User, Group
from senior_advocate.models import AdvocateRegistration
from student.models import LawStudent
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from mail.mailer import send_email
from django_user_agents.utils import get_user_agent
from django.contrib.auth import authenticate
import pytz

class AdvocateRegistrationSerializer(ModelSerializer):
    id_card = FileField(required=True)
    govt_id_proof = FileField(required=True)
    enrollment_date = DateField(required=True)
    date_of_birth = DateField(required=True)
    fathers_name = CharField(max_length=100, required=True)
    mothers_name = CharField(max_length=100, required=True)
    bar_council_name = CharField(max_length=150, required=True)
    enrollment_roll_no = CharField(max_length=100, required=True)
    place_of_practice = CharField(max_length=200, required=True)
    area_of_practice = CharField(max_length=200, required=True)
    communication_address = CharField(required=True)
    contact_number = CharField(max_length=15, required=True)
    spouse_name = CharField(max_length=100, required=True, allow_blank=True)

    class Meta:
        model = AdvocateRegistration
        fields = [
            'fathers_name', 'mothers_name', 'spouse_name', 'bar_council_name',
            'enrollment_roll_no', 'enrollment_date', 'id_card', 'place_of_practice',
            'area_of_practice', 'date_of_birth', 'communication_address', 'contact_number',
            'govt_id_proof'
        ]

    def validate_enrollment_roll_no(self, value):
        if value and AdvocateRegistration.objects.filter(enrollment_roll_no=value).exists():
            raise ValidationError("Enrollment roll number already exists.")
        return value

    def validate(self, data):
        for field in ['id_card', 'govt_id_proof']:
            file_obj = data.get(field)
            if file_obj and hasattr(file_obj, 'size') and file_obj.size == 0:
                raise ValidationError({field: "The submitted file is empty."})
        return data

class LawStudentRegistrationSerializer(ModelSerializer):
    student_id_card = FileField(required=False, allow_null=True)
    govt_id_proof = FileField(required=False, allow_null=True)
    dob = DateField(required=False, allow_null=True)
    course_type = CharField(max_length=50, required=False, allow_blank=True)
    name = CharField(max_length=100, required=False, allow_blank=True)
    email = CharField(required=False, allow_blank=True)
    mobile_no = CharField(max_length=15, required=False, allow_blank=True)
    fathers_name = CharField(max_length=100, required=False, allow_blank=True)
    mothers_name = CharField(max_length=100, required=False, allow_blank=True)
    institution_name = CharField(max_length=150, required=False, allow_blank=True)
    roll_number = CharField(max_length=100, required=False, allow_blank=True)
    study_year = CharField(max_length=50, required=False, allow_blank=True)
    address = CharField(required=False, allow_blank=True)
    spouse_name = CharField(max_length=100, required=False, allow_blank=True)

    class Meta:
        model = LawStudent
        fields = [
            'name', 'email', 'mobile_no', 'fathers_name', 'mothers_name', 'spouse_name',
            'institution_name', 'course_type', 'roll_number', 'study_year', 'dob',
            'address', 'student_id_card', 'govt_id_proof'
        ]

    def validate_email(self, value):
        if value and LawStudent.objects.filter(email=value).exists():
            raise ValidationError("Email already exists.")
        return value

class RegisterSerializer(ModelSerializer):
    password = CharField(write_only=True, required=True)
    confirm_password = CharField(write_only=True, required=True)
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    email = CharField(required=True)
    role = CharField(required=True, source='last_name')
    advocate_data = AdvocateRegistrationSerializer(required=False)
    student_data = LawStudentRegistrationSerializer(required=False)
    cf_turnstile_response = CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'role', 'advocate_data', 'student_data', 'cf_turnstile_response']

    def validate_cf_turnstile_response(self, value):
        secret_key = "0x4AAAAAABh4oKoRiSIWydVq9RbP07XT2l0"
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": secret_key,
                "response": value,
            }
        )
        result = response.json()
        if not result.get("success"):
            raise ValidationError("Cloudflare verification failed.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError({"detail": "Passwords do not match."})
        
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({"email": "A user with this email already exists."})
        
        if data['last_name'] not in ['advocate', 'student']:
            raise ValidationError({"role": "Role must be 'advocate' or 'student'."})
        
        if data['last_name'] == 'advocate':
            request = self.context.get('request')
            advocate_data = request.POST.get('advocate_data', None)
            advocate_dict = {}
            if advocate_data:
                try:
                    advocate_dict = json.loads(advocate_data)
                except json.JSONDecodeError:
                    raise ValidationError({"advocate_data": "Invalid JSON format for advocate data."})
            if request and request.FILES:
                advocate_dict['id_card'] = request.FILES.get('advocate_data[id_card]', None)
                advocate_dict['govt_id_proof'] = request.FILES.get('advocate_data[govt_id_proof]', None)
            if not advocate_dict:
                raise ValidationError({"advocate_data": "Advocate details are required for advocate role."})
            advocate_serializer = AdvocateRegistrationSerializer(data=advocate_dict)
            if not advocate_serializer.is_valid():
                raise ValidationError({"advocate_data": advocate_serializer.errors})
            data['advocate_data'] = advocate_serializer.validated_data
        
        if data['last_name'] == 'student':
            request = self.context.get('request')
            student_data = request.POST.get('student_data', None)
            student_dict = {}
            if student_data:
                try:
                    student_dict = json.loads(student_data)
                except json.JSONDecodeError:
                    raise ValidationError({"student_data": "Invalid JSON format for student data."})
            if request and request.FILES:
                student_dict['student_id_card'] = request.FILES.get('student_data[student_id_card]', None)
                student_dict['govt_id_proof'] = request.FILES.get('student_data[govt_id_proof]', None)
            if not student_dict:
                raise ValidationError({"student_data": "Student details are required for student role."})
            student_serializer = LawStudentRegistrationSerializer(data=student_dict)
            if not student_serializer.is_valid():
                raise ValidationError({"student_data": student_serializer.errors})
            data['student_data'] = student_serializer.validated_data
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('cf_turnstile_response')
        role = validated_data.pop('last_name')
        advocate_data = validated_data.pop('advocate_data', None)
        student_data = validated_data.pop('student_data', None)

        user = User.objects.create_user(**validated_data)
        
        group_name = 'advocates' if role == 'advocate' else 'students'
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        if role == 'advocate' and advocate_data:
            AdvocateRegistration.objects.create(created_by=user, **advocate_data)
        elif role == 'student' and student_data:
            LawStudent.objects.create(created_by=user, **student_data)

        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "groups": [group.name for group in user.groups.all()]
        })

@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request=request, username=username, password=password)
        
        if user is None:
            pass
        else:
            response = super().post(request, *args, **kwargs)
            
            from django.utils import timezone

        if response.status_code == status.HTTP_200_OK:
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
            user_agent = get_user_agent(request)
            local_tz = pytz.timezone('Asia/Colombo')
            login_time = timezone.now().astimezone(local_tz).strftime('%Y-%m-%d %I:%M:%S %p (%Z)')
            message = f"""
            <p>Dear {user.get_full_name() or user.username},</p>
            <p>We have detected a new login to your account. Below are the details:</p>
            <ul>
                <li><strong>Username</strong>: {user.username}</li>
                <li><strong>Email</strong>: {user.email}</li>
                <li><strong>IP Address</strong>: {ip_address}</li>
                <li><strong>Device</strong>: {user_agent.device.family} ({user_agent.os.family} {user_agent.os.version_string})</li>
                <li><strong>Browser</strong>: {user_agent.browser.family} {user_agent.browser.version_string}</li>
                <li><strong>Login Time</strong>: {login_time}</li>
            </ul>
            <p>If this was not you, please secure your account immediately by changing your password and contacting support.</p>
            <p>Best regards,<br>CLH Team</p>
            """
            send_email(
                subject="New Login Detected for Your Account",
                rich_text_content=message,
                use_thread=True,
                to=[user.email],
            )

        return response