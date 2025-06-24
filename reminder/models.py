from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from client.models import Client
from case.models import Case

class Reminder(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="reminders",
        help_text="Select the client for this reminder"
    )
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="reminders",
        help_text="Select the case for this reminder"
    )
    description = models.CharField(max_length=255, blank=False, null=False, help_text="Enter reminder description")
    date = models.DateField(blank=False, null=False, help_text="Select reminder date")
    time = models.TimeField(blank=False, null=False, help_text="Select reminder time")
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('Once', 'Once'),
            ('Daily', 'Daily'),
            ('Weekly', 'Weekly'),
            ('Fort Nightly', 'Fort Nightly'),
        ],
        default='Once',
        help_text="Select reminder frequency"
    )
    emails = models.TextField(blank=True, null=True, help_text="Enter email addresses (comma-separated)")
    whatsapp = models.TextField(blank=True, null=True, help_text="Enter phone numbers (comma-separated)")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
        ],
        default='active',
        help_text="Select reminder status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select the user who created this reminder",
        related_name="reminders_created"
    )

    panels = [
        FieldPanel("client"),
        FieldPanel("case"),
        FieldPanel("description"),
        FieldPanel("date"),
        FieldPanel("time"),
        FieldPanel("frequency"),
        FieldPanel("emails"),
        FieldPanel("whatsapp"),
        FieldPanel("status"),
        FieldPanel("created_by"),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} for {self.case.title}"

    class Meta:
        verbose_name = "Reminder"
        verbose_name_plural = "Reminders"

class ReminderSnippetViewSet(SnippetViewSet):
    model = Reminder
    icon = 'calendar-check'
    add_to_admin_menu = True
    list_display = ('description', 'client', 'case', 'date', 'time', 'frequency', 'status', 'created_by', 'created_at')
    list_export = ('description', 'client', 'case', 'date', 'time', 'frequency', 'status', 'created_by', 'created_at')
    inspect_view_enabled = True
    list_filter = ('frequency', 'status', 'date', 'created_by')
    search_fields = ('description', 'client__name', 'case__title', 'emails', 'whatsapp', 'created_by__username')

register_snippet(ReminderSnippetViewSet)
