from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from client.models import Client
from case.models import Case
from reminder.models import Reminder
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear, TruncDate, TruncWeek
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'month')
        year = request.query_params.get('year', datetime.now().year)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        aggregation = request.query_params.get('aggregation', 'month')
        entity_type = request.query_params.get('entity_type', 'cases')  # New parameter

        # Total counts
        totals = {
            'total_users': User.objects.count(),
            'total_clients': Client.objects.count(),
            'total_cases': Case.objects.count(),
            'total_reminders': Reminder.objects.count(),
        }

        # Choose the model and date field based on entity_type
        model_config = {
            'cases': {'model': Case, 'date_field': 'created_at', 'label': 'Cases Created'},
            'clients': {'model': Client, 'date_field': 'created_at', 'label': 'Clients Added'},
            'users': {'model': User, 'date_field': 'date_joined', 'label': 'Users Registered'},
            'reminders': {'model': Reminder, 'date_field': 'created_at', 'label': 'Reminders Created'},
        }

        if entity_type not in model_config:
            return Response({'error': 'Invalid entity type'}, status=400)

        config = model_config[entity_type]
        model = config['model']
        date_field = config['date_field']
        label = config['label']

        # Graph data for selected entity over time
        if period == 'month':
            queryset = model.objects.filter(**{f'{date_field}__year': year})
            data_by_period = queryset.annotate(
                period=TruncMonth(date_field)
            ).values('period').annotate(count=Count('id')).order_by('period')
            labels = [item['period'].strftime('%b') for item in data_by_period]
            data = [item['count'] for item in data_by_period]

        elif period == 'year':
            queryset = model.objects.all()
            data_by_period = queryset.annotate(
                period=TruncYear(date_field)
            ).values('period').annotate(count=Count('id')).order_by('period')
            labels = [item['period'].strftime('%Y') for item in data_by_period]
            data = [item['count'] for item in data_by_period]

        elif period == 'custom' and start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = model.objects.filter(**{f'{date_field}__range': [start, end]})

                if aggregation == 'day':
                    data_by_period = queryset.annotate(
                        period=TruncDate(date_field)
                    ).values('period').annotate(count=Count('id')).order_by('period')
                    labels = [item['period'].strftime('%Y-%m-%d') for item in data_by_period]
                    data = [item['count'] for item in data_by_period]

                elif aggregation == 'week':
                    data_by_period = queryset.annotate(
                        period=TruncWeek(date_field)
                    ).values('period').annotate(count=Count('id')).order_by('period')
                    labels = [item['period'].strftime('%Y-%m-%d') for item in data_by_period]
                    data = [item['count'] for item in data_by_period]

                elif aggregation == 'month':
                    data_by_period = queryset.annotate(
                        period=TruncMonth(date_field)
                    ).values('period').annotate(count=Count('id')).order_by('period')
                    labels = [item['period'].strftime('%b %Y') for item in data_by_period]
                    data = [item['count'] for item in data_by_period]

                elif aggregation == 'year':
                    data_by_period = queryset.annotate(
                        period=TruncYear(date_field)
                    ).values('period').annotate(count=Count('id')).order_by('period')
                    labels = [item['period'].strftime('%Y') for item in data_by_period]
                    data = [item['count'] for item in data_by_period]

                else:
                    return Response({'error': 'Invalid aggregation'}, status=400)

            except ValueError:
                return Response({'error': 'Invalid date format'}, status=400)
        else:
            return Response({'error': 'Invalid parameters'}, status=400)

        response_data = {
            'totals': totals,
            'graph_data': {
                'labels': labels,
                'data_series': {
                    'label': label,
                    'data': data
                },
                'period': period,
                'entity_type': entity_type,
            }
        }
        return Response(response_data)
