from rest_framework import serializers
from .models import Advocate
from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

class AdvocateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Password for advocate login (if applicable)"
    )
    create_login = serializers.BooleanField(
        default=False,
        help_text="Check to create a user account for this advocate"
    )
    allow_login = serializers.BooleanField(
        default=True,
        help_text="Check to allow this advocate to log in (controls user active state)"
    )

    class Meta:
        model = Advocate
        fields = [
            'id', 'name', 'email', 'password', 'create_login', 'allow_login', 'mobile_no',
            'barcode_number', 'can_add_cases', 'can_modify_cases', 'can_view_all_cases',
            'can_view_assigned_cases', 'can_view_case_fees', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def validate(self, data):
        if data.get('create_login') and not data.get('password'):
            raise serializers.ValidationError({"password": "Password is required when creating a login."})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        create_login = validated_data.pop('create_login', False)
        allow_login = validated_data.pop('allow_login', True)
        password = validated_data.pop('password', None)

        if create_login:
            if User.objects.filter(email=validated_data['email']).exists():
                raise serializers.ValidationError({"email": "A user with this email already exists."})
            
            junior_group, created = Group.objects.get_or_create(name='junior')
            
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=password,
                first_name=validated_data['name'],
                is_active=allow_login
            )
            user.groups.add(junior_group)
            user.save()
            validated_data['user'] = user

        advocate = Advocate.objects.create(**validated_data)
        return advocate

    def update(self, instance, validated_data):
        create_login = validated_data.pop('create_login', instance.create_login)
        allow_login = validated_data.pop('allow_login', instance.allow_login)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if create_login and not instance.user:
            if User.objects.filter(email=instance.email).exists():
                raise serializers.ValidationError({"email": "A user with this email already exists."})
            
            junior_group, created = Group.objects.get_or_create(name='junior')
            user = User.objects.create_user(
                username=instance.email,
                email=instance.email,
                password=password,
                first_name=instance.name,
                is_active=allow_login
            )
            user.groups.add(junior_group)
            user.save()
            instance.user = user
        elif instance.user:
            instance.user.first_name = instance.name
            instance.user.email = instance.email
            instance.user.username = instance.email
            instance.user.is_active = allow_login
            if password:
                instance.user.set_password(password)
            instance.user.save()

        instance.save()
        return instance

class PublicAdvocateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advocate
        fields = ['name', 'email', 'mobile_no']

class AdvocateListCreateView(generics.ListCreateAPIView):
    queryset = Advocate.objects.all()
    serializer_class = AdvocateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Advocate.objects.filter(created_by=self.request.user)

class AdvocateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Advocate.objects.all()
    serializer_class = AdvocateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Advocate.objects.filter(created_by=self.request.user)

class PublicAdvocateListView(generics.ListAPIView):
    queryset = Advocate.objects.all()
    serializer_class = PublicAdvocateSerializer
    permission_classes = [AllowAny]