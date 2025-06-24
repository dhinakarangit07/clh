from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

class CoworkingRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.CharField(max_length=100, blank=False, null=False, help_text="Location of the coworking space")
    date_needed = models.DateField(blank=False, null=False, help_text="Date the space is needed")
    duration = models.CharField(max_length=50, blank=False, null=False, help_text="Duration of the booking")
    purpose_of_visit = models.TextField(blank=False, null=False, help_text="Purpose of the visit")
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending',
        help_text="Current status of the coworking request"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes (optional)")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this request",
        related_name="coworking_requests_created"
    )

    panels = [
        FieldPanel("location"),
        FieldPanel("date_needed"),
        FieldPanel("duration"),
        FieldPanel("purpose_of_visit"),
        FieldPanel("status"),
        FieldPanel("notes"),
        FieldPanel("created_by"),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Coworking Request for {self.location} ({self.status})"

    class Meta:
        verbose_name = "Coworking Request"
        verbose_name_plural = "Coworking Requests"

class CoworkingRequestSnippetViewSet(SnippetViewSet):
    model = CoworkingRequest
    icon = 'building'
    add_to_admin_menu = True
    list_display = ('location', 'date_needed', 'duration', 'status', 'created_by', 'created_at')
    list_export = ('location', 'date_needed', 'duration', 'purpose_of_visit', 'status', 'notes', 'created_by', 'created_at', 'updated_at')
    inspect_view_enabled = True
    list_filter = ('status', 'created_by')
    search_fields = ('location', 'purpose_of_visit')

register_snippet(CoworkingRequestSnippetViewSet)