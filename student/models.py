from django.db import models
from django.contrib.auth.models import User
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

COURSE_CHOICES = (
    ('3-Year LL.B', '3-Year LL.B'),
    ('5-Year LL.B', '5-Year LL.B'),
)

class LawStudent(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    mobile_no = models.CharField(max_length=15, verbose_name='Mobile No.', blank=True, null=True)
    
    fathers_name = models.CharField(max_length=100, blank=True, null=True)
    mothers_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)

    institution_name = models.CharField(max_length=200, blank=True, null=True)
    course_type = models.CharField(max_length=20, choices=COURSE_CHOICES, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    study_year = models.CharField(max_length=20, blank=True, null=True)

    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    student_id_card = models.FileField(upload_to='student/id_cards/', blank=True)
    govt_id_proof = models.FileField(upload_to='student/id_proofs/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="students_created")

    panels = [
        FieldPanel('name'),
        FieldPanel('email'),
        FieldPanel('mobile_no'),
        FieldPanel('fathers_name'),
        FieldPanel('mothers_name'),
        FieldPanel('spouse_name'),
        FieldPanel('institution_name'),
        FieldPanel('course_type'),
        FieldPanel('roll_number'),
        FieldPanel('study_year'),
        FieldPanel('dob'),
        FieldPanel('address'),
        FieldPanel('student_id_card'),
        FieldPanel('govt_id_proof'),
        FieldPanel('created_by'),
    ]

    def __str__(self):
        return f"{self.name or 'Unnamed'} - {self.course_type or 'No Course'}"

    class Meta:
        verbose_name = "LL.B Student"
        verbose_name_plural = "LL.B Students"

class LawStudentSnippetViewSet(SnippetViewSet):
    model = LawStudent
    icon = 'user'
    add_to_admin_menu = True
    list_display = ('name', 'email', 'mobile_no', 'course_type', 'institution_name', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'institution_name')

register_snippet(LawStudentSnippetViewSet)