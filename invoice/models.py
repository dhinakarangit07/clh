from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from client.models import Client
from wagtail.search import index

class ClientInvoice(index.Indexed, ClusterableModel):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    additional_details = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices_created'
    )

    panels = [
        FieldPanel("client"),
        FieldPanel("amount"),
        FieldPanel("due_date"),
        FieldPanel("reference_no"),
        FieldPanel("additional_details"),
        FieldPanel("created_by"),
        InlinePanel("payments", label="Payments", min_num=0, classname="collapsible collapsed"),
    ]

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = ClientInvoice.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                self.invoice_number = f"INV-{last_number+1:05d}"
            else:
                self.invoice_number = "INV-00001"
        
        if not self.created_by and 'user' in kwargs and hasattr(kwargs['user'], 'pk'):
            self.created_by = kwargs['user']
            
        super().save(*args, **kwargs)

    def get_paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())

    def get_pending_amount(self):
        return self.amount - self.get_paid_amount()

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"

    class Meta:
        verbose_name = "Client Invoice"
        verbose_name_plural = "Client Invoices"

class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = ParentalKey(
        ClientInvoice, 
        on_delete=models.CASCADE, 
        related_name='payments',
        help_text="The invoice this payment belongs to."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    )
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payments_created'
    )

    panels = [
        FieldPanel("amount"),
        FieldPanel("payment_date"),
        FieldPanel("payment_mode"),
        FieldPanel("reference_no"),
        FieldPanel("remarks"),
        FieldPanel("created_by", read_only=True),
    ]

    def save(self, *args, **kwargs):
        if not self.created_by and 'user' in kwargs and hasattr(kwargs['user'], 'pk'):
            self.created_by = kwargs['user']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id} for {self.invoice.invoice_number}"

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['created_at']

class ClientInvoiceSnippetViewSet(SnippetViewSet):
    model = ClientInvoice
    icon = 'doc-full-inverse'
    add_to_admin_menu = True
    list_display = ('invoice_number', 'client', 'amount', 'due_date', 'created_by', 'created_at')
    list_export = list_display
    inspect_view_enabled = True
    list_filter = ('due_date', 'created_by')
    search_fields = ('invoice_number', 'client__name', 'reference_no')

register_snippet(ClientInvoiceSnippetViewSet)