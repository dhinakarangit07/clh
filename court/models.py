from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

class Court(models.Model):
    STATE_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    court = models.CharField(max_length=200)
    advocate_name = models.CharField(max_length=200)
    state_code = models.CharField(max_length=20)
    bar_code_number = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    last_sync = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATE_CHOICES, default="active")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courts_created'
    )

    panels = [
        FieldPanel("state"),
        FieldPanel("district"),
        FieldPanel("court"),
        FieldPanel("advocate_name"),
        FieldPanel("state_code"),
        FieldPanel("bar_code_number"),
        FieldPanel("year"),
        FieldPanel("status"),
        FieldPanel("created_by"),
    ]

    def save(self, *args, **kwargs):
        if not self.created_by and 'user' in kwargs and hasattr(kwargs['user'], 'pk'):
            self.created_by = kwargs['user']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.state} - {self.district} - {self.court}"

    class Meta:
        verbose_name = "Court Entry"
        verbose_name_plural = "Court Entries"

class CourtSnippetViewSet(SnippetViewSet):
    model = Court
    icon = 'doc-full-inverse'
    add_to_admin_menu = True
    list_display = ('state', 'district', 'court', 'advocate_name', 'status', 'created_by', 'last_sync')
    list_export = list_display
    inspect_view_enabled = True
    list_filter = ('status', 'created_by')
    search_fields = ('state', 'district', 'court', 'advocate_name', 'state_code', 'bar_code_number')

register_snippet(CourtSnippetViewSet)