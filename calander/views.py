from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from case.models import Case
from reminder.models import Reminder
from client.models import Client
from datetime import datetime
from django.utils.dateparse import parse_date

# Custom permission for advocates group
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='advocates').exists()

# Custom permission for client group
class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='client').exists()

class CalendarEventSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    time = serializers.CharField()
    location = serializers.CharField()
    type = serializers.CharField()
    client = serializers.CharField()
    priority = serializers.CharField()
    date = serializers.DateField()

class CaseEventSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    time = serializers.SerializerMethodField()
    location = serializers.CharField(source='court')
    type = serializers.CharField(default='hearing')
    client = serializers.CharField(source='client.name')
    priority = serializers.CharField(default='high')
    date = serializers.DateField(source='next_hearing')

    class Meta:
        model = Case
        fields = ['id', 'title', 'time', 'location', 'type', 'client', 'priority', 'date']

    def get_time(self, obj):
        return 'N/A'

class ReminderEventSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(source='description')
    time = serializers.SerializerMethodField()
    location = serializers.CharField(default='N/A')
    type = serializers.CharField(default='reminder')
    client = serializers.CharField(source='client.name')
    priority = serializers.CharField(default='medium')
    date = serializers.DateField()

    class Meta:
        model = Reminder
        fields = ['id', 'title', 'time', 'location', 'type', 'client', 'priority', 'date']

    def get_time(self, obj):
        return obj.time.strftime('%I:%M %p') if obj.time else 'N/A'

class CalendarEventsView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start_date = parse_date(start_date_str) if start_date_str else datetime.now().date()
            end_date = parse_date(end_date_str) if end_date_str else start_date
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch cases with next hearing in the date range
        cases = Case.objects.filter(
            created_by=request.user,
            next_hearing__range=[start_date, end_date],
            next_hearing__isnull=False
        )
        case_events = CaseEventSerializer(cases, many=True).data

        # Fetch reminders in the date range
        reminders = Reminder.objects.filter(
            created_by=request.user,
            date__range=[start_date, end_date],
            status='active'
        )
        reminder_events = ReminderEventSerializer(reminders, many=True).data

        # Combine and group by date
        events_by_date = {}
        for event in case_events + reminder_events:
            date_str = event['date']
            if date_str not in events_by_date:
                events_by_date[date_str] = []
            events_by_date[date_str].append(event)

        return Response(events_by_date, status=status.HTTP_200_OK)

class ClientCalendarEventsView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start_date = parse_date(start_date_str) if start_date_str else datetime.now().date()
            end_date = parse_date(end_date_str) if end_date_str else start_date
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(user=request.user)
            # Fetch cases with next hearing in the date range for the client
            cases = Case.objects.filter(
                client=client,
                next_hearing__range=[start_date, end_date],
                next_hearing__isnull=False
            )
            case_events = CaseEventSerializer(cases, many=True).data

            # Fetch reminders in the date range for the client's cases
            reminders = Reminder.objects.filter(
                case__client=client,
                date__range=[start_date, end_date],
                status='active'
            )
            reminder_events = ReminderEventSerializer(reminders, many=True).data

            # Combine and group by date
            events_by_date = {}
            for event in case_events + reminder_events:
                date_str = event['date']
                if date_str not in events_by_date:
                    events_by_date[date_str] = []
                events_by_date[date_str].append(event)

            return Response(events_by_date, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response({"error": "Client profile not found."}, status=status.HTTP_404_NOT_FOUND)