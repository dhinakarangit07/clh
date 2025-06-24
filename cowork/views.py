from rest_framework import serializers
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from .models import CoworkingRequest
from django.contrib.auth.models import User

# Custom permission for advocates group
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='advocates').exists()

class CoworkingRequestSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    status = serializers.CharField()  # Allow case-insensitive status for frontend compatibility

    class Meta:
        model = CoworkingRequest
        fields = [
            'id', 'location', 'date_needed', 'duration', 'purpose_of_visit', 'status',
            'created_at', 'updated_at', 'notes', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        """
        Validate input data.
        """
        # Ensure status is one of the allowed choices (case-insensitive)
        status = data.get('status', 'Pending').capitalize()
        if status not in ['Pending', 'Approved', 'Rejected']:
            raise serializers.ValidationError("Status must be one of: Pending, Approved, Rejected.")
        data['status'] = status

        # Validate date_needed is not in the past
        from datetime import date
        date_needed = data.get('date_needed')
        if date_needed and date_needed < date.today():
            raise serializers.ValidationError("Date needed cannot be in the past.")

        return data

    def to_representation(self, instance):
        """
        Convert status to lowercase for frontend compatibility.
        """
        ret = super().to_representation(instance)
        ret['status'] = ret['status'].lower()  # Match frontend's 'approved', 'pending', 'rejected'
        return ret

class CoworkingRequestListCreateView(generics.ListCreateAPIView):
    queryset = CoworkingRequest.objects.all()
    serializer_class = CoworkingRequestSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return CoworkingRequest.objects.filter(created_by=self.request.user).order_by('-created_at')

class CoworkingRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoworkingRequest.objects.all()
    serializer_class = CoworkingRequestSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return CoworkingRequest.objects.filter(created_by=self.request.user)

class CoworkingRequestCheckView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request, *args, **kwargs):
        try:
            # Get the latest coworking request for the authenticated user
            coworking_request = CoworkingRequest.objects.filter(
                created_by=request.user
            ).order_by('-created_at').first()
            
            if coworking_request:
                serializer = CoworkingRequestSerializer(coworking_request, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"exists": False}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )