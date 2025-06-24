from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.search import index
from advocate.models import Advocate

class UploadedFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = ParentalKey(
        'Task',
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        help_text="Task associated with this file"
    )
    name = models.CharField(max_length=255, help_text="Name of the uploaded file")
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', help_text="The uploaded file")
    size = models.PositiveIntegerField(help_text="Size of the file in bytes")
    type = models.CharField(max_length=100, help_text="MIME type of the file")
    uploaded_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when file was uploaded")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who uploaded the file",
        related_name='uploaded_files'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('file'),
        FieldPanel('size'),
        FieldPanel('type'),
        FieldPanel('created_by', read_only=True),
        FieldPanel('uploaded_at', read_only=True),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"

class Task(index.Indexed, ClusterableModel):
    DOCUMENT_TYPE_CHOICES = [
        ('NDA', 'NDA'),
        ('Contract', 'Contract'),
        ('Agreement', 'Agreement'),
        ('Legal Brief', 'Legal Brief'),
        ('Other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('feedback_required', 'Feedback Required'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=False, null=False, help_text="Task title")
    description = models.TextField(blank=True, null=True, help_text="Task description")
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='Other',
        help_text="Type of document"
    )
    start_date = models.DateField(blank=True, null=True, help_text="Start date of the task")
    review_date = models.DateField(blank=True, null=True, help_text="Date for review")
    deadline = models.DateField(blank=True, null=True, help_text="Task deadline")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low',
        help_text="Task priority"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Task status"
    )
    review_feedback = models.TextField(blank=True, null=True, help_text="Feedback from review")
    nda_details = models.TextField(blank=True, null=True, help_text="NDA-specific details")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created the task",
        related_name='tasks_created'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User assigned to this task",
        related_name='tasks_assigned'
    )
    assigned_junior_advocate = models.ForeignKey(
        Advocate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Junior advocate assigned to this task",
        related_name='tasks_assigned_junior'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('document_type'),
        FieldPanel('start_date'),
        FieldPanel('review_date'),
        FieldPanel('deadline'),
        FieldPanel('priority'),
        FieldPanel('status'),
        FieldPanel('review_feedback'),
        FieldPanel('nda_details'),
        FieldPanel('created_by', read_only=True),
        FieldPanel('assigned_to'),
        FieldPanel('assigned_junior_advocate'),
        InlinePanel('uploaded_files', label="Uploaded Files", min_num=0, classname="collapsible collapsed"),
    ]

    search_fields = [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('nda_details'),
        index.SearchField('review_feedback'),
        index.FilterField('created_by'),
        index.FilterField('assigned_to'),
        index.FilterField('assigned_junior_advocate'),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

class TaskSnippetViewSet(SnippetViewSet):
    model = Task
    icon = 'tasks'
    add_to_admin_menu = True
    list_display = ('title', 'document_type', 'priority', 'status', 'deadline', 'created_by', 'assigned_to', 'assigned_junior_advocate', 'created_at')
    list_export = ('title', 'description', 'document_type', 'start_date', 'review_date', 'deadline', 'priority', 'status', 'review_feedback', 'nda_details', 'created_by', 'assigned_to', 'assigned_junior_advocate', 'created_at', 'updated_at')
    inspect_view_enabled = True
    list_filter = ('document_type', 'priority', 'status', 'created_by', 'assigned_to', 'assigned_junior_advocate', 'created_at')
    search_fields = ('title', 'description', 'nda_details', 'review_feedback', 'created_by__username', 'assigned_to__username', 'assigned_junior_advocate__name')

register_snippet(TaskSnippetViewSet)