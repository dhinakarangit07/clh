from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Court

class StateSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    version = serializers.CharField()

class DistrictSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()

class ComplexSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()

class CourtSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()

class CourtSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Court
        fields = [
            'id', 'state', 'district', 'court', 'advocate_name', 'state_code',
            'bar_code_number', 'year', 'last_sync', 'status', 'created_by'
        ]
        read_only_fields = ['id', 'last_sync', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)




import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import Court

BASE_URL = "https://phoenix.akshit.me/district-court"

# Fetch states from Phoenix API
class StateFetchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            response = requests.post(f"{BASE_URL}/states", json={}, timeout=10)
            response.raise_for_status()
            data = response.json()

            states_list = data.get('states', [])
            serializer = StateSerializer(states_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Fetch districts based on state_id
class DistrictFetchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            state_external_id = request.data.get('stateId')
            if not state_external_id:
                return Response({"error": "stateId is required"}, status=status.HTTP_400_BAD_REQUEST)

            payload = {"stateId": state_external_id}
            response = requests.post(f"{BASE_URL}/districts", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            districts_list = data.get('districts', [])
            serializer = DistrictSerializer(districts_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Fetch courts based on district_id
class CourtFetchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            district_external_id = request.data.get('districtId')
            if not district_external_id:
                return Response({"error": "districtId is required"}, status=status.HTTP_400_BAD_REQUEST)

            payload = {"districtId": district_external_id}
            response = requests.post(f"{BASE_URL}/courts", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            courts_list = data.get('courts', [])
            serializer = CourtSerializer(courts_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Fetch complexes based on district_id
class ComplexFetchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            district_external_id = request.data.get('district_id')
            if not district_external_id:
                return Response({"error": "district_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            payload = {"districtId": district_external_id}
            response = requests.post(f"{BASE_URL}/complexes", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            complexes_list = data.get('complexes', [])
            serializer = ComplexSerializer(complexes_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Create and List Court Entries
class CourtListCreateView(generics.ListCreateAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Court.objects.filter(created_by=self.request.user)

# Retrieve, Update, Delete Court Entry
class CourtRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Court.objects.filter(created_by=self.request.user)