from rest_framework import serializers
from .models import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class ClientSerializer(serializers.ModelSerializer):
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
        help_text="Password for client login (if applicable)"
    )
    create_login = serializers.BooleanField(
        default=False,
        help_text="Check to create a user account for this client"
    )
    allow_login = serializers.BooleanField(
        default=True,
        help_text="Check to allow this client to log in (controls user active state)"
    )
    is_corporate = serializers.BooleanField(
        default=False,
        help_text="Check if this client is a corporate entity"
    )
    payment_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total payment amount for the client"
    )

    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'password', 'create_login', 'allow_login', 'contact_number', 'address', 'created_at', 'created_by', 'is_corporate', 'payment_amount']
        read_only_fields = ['id', 'created_at', 'created_by']

    def validate(self, data):
        # Require password when create_login is True during creation or update
        if data.get('create_login') and not data.get('password'):
            raise serializers.ValidationError({"password": "Password is required when creating a login."})
        # Ensure payment_amount is non-negative
        if data.get('payment_amount') is not None and data.get('payment_amount') < 0:
            raise serializers.ValidationError({"payment_amount": "Payment amount cannot be negative."})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        create_login = validated_data.pop('create_login', False)
        allow_login = validated_data.pop('allow_login', True)
        password = validated_data.pop('password', None)
        is_corporate = validated_data.pop('is_corporate', False)
        payment_amount = validated_data.pop('payment_amount', 0.00)

        if create_login:
            if User.objects.filter(email=validated_data['email']).exists():
                raise serializers.ValidationError({"email": "A user with this email already exists."})
            
            client_group, created = Group.objects.get_or_create(name='client')
            
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=password,
                first_name=validated_data['name'],
                is_active=allow_login
            )
            user.groups.add(client_group)
            user.save()
            validated_data['user'] = user  # Link the user to the client

        client = Client.objects.create(
            **validated_data,
            is_corporate=is_corporate,
            payment_amount=payment_amount
        )
        return client

    def update(self, instance, validated_data):
        create_login = validated_data.pop('create_login', instance.create_login)
        allow_login = validated_data.pop('allow_login', instance.allow_login)
        password = validated_data.pop('password', None)
        is_corporate = validated_data.pop('is_corporate', instance.is_corporate)
        payment_amount = validated_data.pop('payment_amount', instance.payment_amount)

        # Update client instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.is_corporate = is_corporate
        instance.payment_amount = payment_amount

        # Handle user creation or update
        if create_login and not instance.user:
            # Create new user if create_login is True and no user exists
            if User.objects.filter(email=instance.email).exists():
                raise serializers.ValidationError({"email": "A user with this email already exists."})
            
            client_group, created = Group.objects.get_or_create(name='client')
            user = User.objects.create_user(
                username=instance.email,
                email=instance.email,
                password=password,
                first_name=instance.name,
                is_active=allow_login
            )
            user.groups.add(client_group)
            user.save()
            instance.user = user
        elif instance.user:
            # Update existing user
            instance.user.first_name = instance.name
            instance.user.email = instance.email
            instance.user.username = instance.email
            instance.user.is_active = allow_login
            if password:
                instance.user.set_password(password)
            instance.user.save()

        instance.save()
        return instance

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Client

class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(created_by=self.request.user)

class ClientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(created_by=self.request.user)