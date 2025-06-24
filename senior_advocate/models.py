from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class AdvocateRegistration(models.Model):
    id = models.BigAutoField(primary_key=True)

    fathers_name = models.CharField(max_length=100, blank=True, null=True)
    mothers_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    bar_council_name = models.CharField(max_length=150, blank=True, null=True)
    enrollment_roll_no = models.CharField(max_length=100, blank=True, null=True, unique=True)
    enrollment_date = models.DateField(blank=True, null=True)
    id_card = models.FileField(upload_to='advocates/id_cards/', blank=True, null=True)
    place_of_practice = models.CharField(max_length=200, blank=True, null=True)
    area_of_practice = models.CharField(max_length=200, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    communication_address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    govt_id_proof = models.FileField(upload_to='advocates/govt_ids/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advocate_registrations_created'
    )

    panels = [
        FieldPanel("fathers_name"),
        FieldPanel("mothers_name"),
        FieldPanel("spouse_name"),
        FieldPanel("bar_council_name"),
        FieldPanel("enrollment_roll_no"),
        FieldPanel("enrollment_date"),
        FieldPanel("id_card"),
        FieldPanel("place_of_practice"),
        FieldPanel("area_of_practice"),
        FieldPanel("date_of_birth"),
        FieldPanel("communication_address"),
        FieldPanel("contact_number"),
        FieldPanel("govt_id_proof"),
        FieldPanel("created_by"),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment_roll_no or 'N/A'} - {self.fathers_name or 'N/A'}"

    class Meta:
        verbose_name = "Senior Advocate"
        verbose_name_plural = "Senior Advocates"


class AdvocateRegistrationSnippetViewSet(SnippetViewSet):
    model = AdvocateRegistration
    icon = 'form'
    add_to_admin_menu = True
    list_display = (
        'enrollment_roll_no', 'fathers_name', 'bar_council_name',
        'contact_number', 'created_by', 'created_at'
    )
    list_export = (
        'enrollment_roll_no', 'fathers_name', 'mothers_name', 'spouse_name',
        'bar_council_name', 'enrollment_date', 'place_of_practice', 'area_of_practice',
        'date_of_birth', 'communication_address', 'contact_number',
        'created_by', 'created_at'
    )
    inspect_view_enabled = True
    list_filter = ('enrollment_date', 'bar_council_name', 'created_by')
    search_fields = (
        'enrollment_roll_no', 'fathers_name', 'bar_council_name',
        'contact_number', 'created_by__username'
    )


register_snippet(AdvocateRegistrationSnippetViewSet)