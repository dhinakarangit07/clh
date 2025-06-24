from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from client.models import Client
from advocate.models import Advocate

class Case(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=False, null=False, help_text="Enter case title")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="cases",
        blank=True, null=True,
        help_text="Select the client for this case"
    )
    advocate = models.ForeignKey(
        Advocate,
        on_delete=models.SET_NULL,
        related_name="cases",
        blank=True, null=True,
        help_text="Select the advocate for this case (optional)"
    )
    type = models.CharField(
        max_length=50,
        choices=[
            ('Civil', 'Civil'),
            ('Criminal', 'Criminal'),
            ('Corporate', 'Corporate'),
            ('Estate', 'Estate'),
            ('Commercial', 'Commercial'),
            ('Tax', 'Tax'),
        ],
        blank=False,
        null=False,
        help_text="Select case type"
    )
    court = models.CharField(max_length=255, blank=True, null=True, help_text="Enter court name")
    case_number = models.CharField(max_length=50, blank=False, null=False, unique=True, help_text="Enter case number")
    cnr_number = models.CharField(max_length=50, blank=True, null=True, help_text="Enter CNR number (e.g., MHAU010123452014)")
    file_no = models.CharField(max_length=50, blank=True, null=True, help_text="Enter file number")
    file_name = models.CharField(max_length=255, blank=True, null=True, help_text="Enter file name")
    reference_no = models.CharField(max_length=50, blank=True, null=True, help_text="Enter reference number")
    year = models.CharField(max_length=4, blank=True, null=True, help_text="Enter year (e.g., 2025)")
    fir_no = models.CharField(max_length=50, blank=True, null=True, help_text="Enter FIR number")
    first_party = models.CharField(max_length=255, blank=True, null=True, help_text="Enter first party")
    under_section = models.CharField(max_length=100, blank=True, null=True, help_text="Enter section under which case is filed")
    opposite_party = models.CharField(max_length=255, blank=True, null=True, help_text="Enter opposite party")
    stage_of_case = models.CharField(max_length=255, blank=True, null=True, help_text="Enter stage of case or fixed for")
    judge_name = models.CharField(max_length=255, blank=True, null=True, help_text="Enter judge name")
    next_hearing = models.DateField(blank=True, null=True, help_text="Select next hearing date")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('pending', 'Pending'),
            ('decided', 'Decided'),
            ('abandoned', 'Abandoned'),
            ('assigned', 'Assigned'),
        ],
        default='pending',
        help_text="Select case status"
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        default='medium',
        help_text="Select case priority"
    )
    last_update = models.DateField(auto_now=True, help_text="Last updated date")
    description = models.TextField(blank=True, null=True, help_text="Enter case description")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select the user who created this case",
        related_name="cases_created"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("client"),
        FieldPanel("advocate"),
        FieldPanel("type"),
        FieldPanel("court"),
        FieldPanel("case_number"),
        FieldPanel("cnr_number"),
        FieldPanel("file_no"),
        FieldPanel("file_name"),
        FieldPanel("reference_no"),
        FieldPanel("year"),
        FieldPanel("fir_no"),
        FieldPanel("first_party"),
        FieldPanel("under_section"),
        FieldPanel("opposite_party"),
        FieldPanel("stage_of_case"),
        FieldPanel("judge_name"),
        FieldPanel("next_hearing"),
        FieldPanel("status"),
        FieldPanel("priority"),
        FieldPanel("description"),
        FieldPanel("created_by"),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Case"
        verbose_name_plural = "Cases"

class CaseSnippetViewSet(SnippetViewSet):
    model = Case
    icon = 'doc-full'
    add_to_admin_menu = True
    list_display = ('title',)
    list_export = ('title', 'client', 'advocate', 'type', 'case_number', 'cnr_number', 'file_no', 'reference_no', 'fir_no', 'status', 'priority', 'created_by', 'created_at')
    inspect_view_enabled = True
    list_filter = ('type', 'status', 'priority', 'created_at', 'created_by')
    search_fields = ('title', 'client__name', 'advocate__name', 'case_number', 'cnr_number', 'file_no', 'reference_no', 'fir_no', 'court', 'first_party', 'under_section', 'opposite_party', 'stage_of_case', 'judge_name', 'created_by__username')

register_snippet(CaseSnippetViewSet)