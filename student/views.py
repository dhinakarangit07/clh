from rest_framework import serializers
from .models import LawStudent

class LawStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawStudent
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')



from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import LawStudent


class LawStudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = LawStudent.objects.all().order_by('-created_at')
    serializer_class = LawStudentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # Change as needed

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

class LawStudentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LawStudent.objects.all()
    serializer_class = LawStudentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # Change as needed
