from rest_framework import serializers
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from .models import HandbagRequest
from django.contrib.auth.models import User

# Custom permission for advocates group
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='advocates').exists()

class HandbagRequestSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = HandbagRequest
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'address1', 'address2',
            'district', 'state', 'pin_code', 'status', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        """
        Validate PIN code format.
        """
        pin_code = data.get('pin_code')
        if pin_code and not pin_code.isdigit():
            raise serializers.ValidationError("PIN code must contain only digits.")
        return data

class HandbagRequestListCreateView(generics.ListCreateAPIView):
    queryset = HandbagRequest.objects.all()
    serializer_class = HandbagRequestSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return HandbagRequest.objects.filter(created_by=self.request.user)

class HandbagRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HandbagRequest.objects.all()
    serializer_class = HandbagRequestSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return HandbagRequest.objects.filter(created_by=self.request.user)

class HandbagRequestCheckView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request, *args, **kwargs):
        try:
            # Get the latest handbag request for the authenticated user
            handbag_request = HandbagRequest.objects.filter(
                created_by=request.user
            ).order_by('-created_at').first()
            
            if handbag_request:
                serializer = HandbagRequestSerializer(handbag_request, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"exists": False}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )