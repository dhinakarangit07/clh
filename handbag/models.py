from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

class HandbagRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100, blank=False, null=False, help_text="First name of the requester")
    last_name = models.CharField(max_length=100, blank=False, null=False, help_text="Last name of the requester")
    email = models.EmailField(blank=False, null=False, help_text="Email address of the requester")
    phone = models.CharField(max_length=20, blank=False, null=False, help_text="Phone number of the requester")
    address1 = models.CharField(max_length=255, blank=False, null=False, help_text="Primary address line")
    address2 = models.CharField(max_length=255, blank=True, null=True, help_text="Secondary address line (optional)")
    district = models.CharField(max_length=100, blank=False, null=False, help_text="District of the requester")
    state = models.CharField(max_length=100, blank=False, null=False, help_text="State of the requester")
    pin_code = models.CharField(max_length=10, blank=False, null=False, help_text="PIN code of the requester")
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Processing', 'Processing'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
        ],
        default='Pending',
        help_text="Current status of the handbag request"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this request",
        related_name="handbag_requests_created"
    )

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("email"),
        FieldPanel("phone"),
        FieldPanel("address1"),
        FieldPanel("address2"),
        FieldPanel("district"),
        FieldPanel("state"),
        FieldPanel("pin_code"),
        FieldPanel("status"),
        FieldPanel("created_by"),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Handbag Request for {self.first_name} {self.last_name} ({self.status})"

    class Meta:
        verbose_name = "Handbag Request"
        verbose_name_plural = "Handbag Requests"

class HandbagRequestSnippetViewSet(SnippetViewSet):
    model = HandbagRequest
    icon = 'package'
    add_to_admin_menu = True
    list_display = ('first_name', 'last_name', 'email', 'phone', 'status', 'created_by', 'created_at')
    list_export = ('first_name', 'last_name', 'email', 'phone', 'address1', 'address2', 'district', 'state', 'pin_code', 'status', 'created_by', 'created_at')
    inspect_view_enabled = True
    list_filter = ('status', 'created_by')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'address1', 'district', 'state')

register_snippet(HandbagRequestSnippetViewSet)