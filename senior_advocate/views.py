
from rest_framework import serializers
from .models import AdvocateRegistration
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group
from user_profile.models import Profile
from wagtail.images.models import Image

# Existing AdvocateRegistrationSerializer
class AdvocateRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocateRegistration
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')

# Updated serializer for advocate users
class AdvocateUserSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'photo')

    def get_photo(self, obj):
        try:
            profile = obj.profile
            if profile.photo:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(profile.photo.get_rendition('max-200x200').url)
                return profile.photo.get_rendition('max-200x200').url
        except Profile.DoesNotExist:
            pass
        return None

# Updated serializer for advocate details with user info
class AdvocateRegistrationDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='created_by.email', read_only=True)
    user_first_name = serializers.CharField(source='created_by.first_name', read_only=True)
    user_last_name = serializers.CharField(source='created_by.last_name', read_only=True)
    user_photo = serializers.SerializerMethodField()

    class Meta:
        model = AdvocateRegistration
        fields = (
            'user_email', 'user_first_name', 'user_last_name', 'user_photo',
            'fathers_name', 'mothers_name', 'spouse_name',
            'bar_council_name', 'enrollment_roll_no', 'enrollment_date',
            'place_of_practice', 'area_of_practice', 'date_of_birth',
            'communication_address', 'contact_number', 'created_at'
        )

    def get_user_photo(self, obj):
        try:
            profile = obj.created_by.profile
            if profile.photo:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(profile.photo.get_rendition('max-200x200').url)
                return profile.photo.get_rendition('max-200x200').url
        except Profile.DoesNotExist:
            pass
        return None

# Existing AdvocateRegistrationListCreateAPIView
class AdvocateRegistrationListCreateAPIView(generics.ListCreateAPIView):
    queryset = AdvocateRegistration.objects.all().order_by('-created_at')
    serializer_class = AdvocateRegistrationSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

# Existing AdvocateRegistrationRetrieveUpdateDestroyAPIView
class AdvocateRegistrationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdvocateRegistration.objects.all()
    serializer_class = AdvocateRegistrationSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

# Updated view for listing advocate group users
class AdvocateUsersListAPIView(generics.ListAPIView):
    serializer_class = AdvocateUserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        try:
            advocate_group = Group.objects.get(name='advocates')
            return User.objects.filter(groups=advocate_group).order_by('email')
        except Group.DoesNotExist:
            return User.objects.none()

    def get_serializer_context(self):
        return {'request': self.request}

# Updated view for getting advocate details by email
class AdvocateDetailsByEmailAPIView(generics.RetrieveAPIView):
    serializer_class = AdvocateRegistrationDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'email'

    def get_queryset(self):
        email = self.kwargs.get('email')
        return AdvocateRegistration.objects.filter(created_by__email=email)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().first()
            if not instance:
                return Response(
                    {"detail": "No advocate found with this email address."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(instance, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
