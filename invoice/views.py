from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
from .models import ClientInvoice, Payment
from client.models import Client
from .pdf_utils import generate_invoice_pdf

# Custom permission for advocates group
class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='advocates').exists()

# Custom permission for client group
class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='client').exists()

class PaymentSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'payment_date', 'payment_mode',
            'reference_no', 'remarks', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

class ClientInvoiceSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all()
    )
    payments = PaymentSerializer(many=True, required=False)
    paid_amount = serializers.SerializerMethodField()
    pending_amount = serializers.SerializerMethodField()

    class Meta:
        model = ClientInvoice
        fields = [
            'id', 'invoice_number', 'client', 'amount', 'due_date',
            'reference_no', 'additional_details', 'created_at',
            'created_by', 'payments', 'paid_amount', 'pending_amount'
        ]
        read_only_fields = ['id', 'invoice_number', 'created_at', 'created_by', 'paid_amount', 'pending_amount']

    def get_paid_amount(self, obj):
        return obj.get_paid_amount()

    def get_pending_amount(self, obj):
        return obj.get_pending_amount()

    def create(self, validated_data):
        request = self.context.get('request')
        payments_data = validated_data.pop('payments', [])
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        instance = super().create(validated_data)
        
        for payment_data in payments_data:
            payment_data['created_by'] = request.user
            Payment.objects.create(invoice=instance, **payment_data)
        
        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request')
        payments_data = validated_data.pop('payments', [])
        
        instance = super().update(instance, validated_data)
        
        existing_payment_ids = [payment.id for payment in instance.payments.all()]
        new_payment_ids = [payment_data.get('id') for payment_data in payments_data if payment_data.get('id')]
        
        instance.payments.exclude(id__in=new_payment_ids).delete()
        
        for payment_data in payments_data:
            payment_id = payment_data.get('id')
            payment_data['created_by'] = request.user
            if payment_id and Payment.objects.filter(id=payment_id, invoice=instance).exists():
                payment = Payment.objects.get(id=payment_id)
                for key, value in payment_data.items():
                    if key != 'id':
                        setattr(payment, key, value)
                payment.save()
            else:
                Payment.objects.create(invoice=instance, **payment_data)
        
        return instance

class ClientInvoiceListCreateView(generics.ListCreateAPIView):
    queryset = ClientInvoice.objects.all()
    serializer_class = ClientInvoiceSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return ClientInvoice.objects.filter(created_by=self.request.user)

class ClientInvoiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClientInvoice.objects.all()
    serializer_class = ClientInvoiceSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return ClientInvoice.objects.filter(created_by=self.request.user)

class ClientInvoiceListView(generics.ListAPIView):
    serializer_class = ClientInvoiceSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        try:
            client = Client.objects.get(user=self.request.user)
            return ClientInvoice.objects.filter(client=client)
        except Client.DoesNotExist:
            return ClientInvoice.objects.none()

class ClientInvoiceRetrieveView(generics.RetrieveAPIView):
    serializer_class = ClientInvoiceSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        try:
            client = Client.objects.get(user=self.request.user)
            return ClientInvoice.objects.filter(client=client)
        except Client.DoesNotExist:
            return ClientInvoice.objects.none()

def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(ClientInvoice, id=invoice_id)
    response = HttpResponse(content_type='application/pdf')
    return generate_invoice_pdf(invoice, response, is_download=True)

def print_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(ClientInvoice, id=invoice_id)
    response = HttpResponse(content_type='application/pdf')
    return generate_invoice_pdf(invoice, response, is_download=False)

def client_download_invoice_pdf(request, invoice_id):
    try:
        client = Client.objects.get(user=request.user)
        invoice = get_object_or_404(ClientInvoice, id=invoice_id, client=client)
        response = HttpResponse(content_type='application/pdf')
        return generate_invoice_pdf(invoice, response, is_download=True)
    except Client.DoesNotExist:
        return HttpResponse("Client profile not found.", status=404)

def client_print_invoice_pdf(request, invoice_id):
    try:
        client = Client.objects.get(user=request.user)
        invoice = get_object_or_404(ClientInvoice, id=invoice_id, client=client)
        response = HttpResponse(content_type='application/pdf')
        return generate_invoice_pdf(invoice, response, is_download=False)
    except Client.DoesNotExist:
        return HttpResponse("Client profile not found.", status=404)