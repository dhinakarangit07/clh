from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

class Advocate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False, help_text="Enter advocate name")
    email = models.EmailField(blank=False, null=False, help_text="Enter email address")
    password = models.CharField(max_length=128, blank=True, null=True, help_text="Enter password for advocate login (if applicable)")
    create_login = models.BooleanField(default=False, help_text="Check to create a user account for this advocate")
    allow_login = models.BooleanField(default=True, help_text="Check to allow this advocate to log in (controls user active state)")
    mobile_no = models.CharField(max_length=20, blank=True, null=True, help_text="Enter mobile number for SMS alerts")
    barcode_number = models.CharField(max_length=50, blank=True, null=True, help_text="Enter barcode number")
    can_add_cases = models.BooleanField(default=False, help_text="Allow advocate to add cases")
    can_modify_cases = models.BooleanField(default=False, help_text="Allow advocate to modify cases")
    can_view_all_cases = models.BooleanField(default=False, help_text="Allow advocate to view all cases")
    can_view_assigned_cases = models.BooleanField(default=False, help_text="Allow advocate to view only assigned cases")
    can_view_case_fees = models.BooleanField(default=False, help_text="Allow advocate to view case fees")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select the user who created this advocate",
        related_name="advocates_created"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The user account associated with this advocate",
        related_name="advocate_profile"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("password"),
        FieldPanel("create_login"),
        FieldPanel("allow_login"),
        FieldPanel("mobile_no"),
        FieldPanel("barcode_number"),
        FieldPanel("can_add_cases"),
        FieldPanel("can_modify_cases"),
        FieldPanel("can_view_all_cases"),
        FieldPanel("can_view_assigned_cases"),
        FieldPanel("can_view_case_fees"),
        FieldPanel("created_by"),
        FieldPanel("user"),
    ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.created_by and hasattr(kwargs.get('user'), 'pk'):
            self.created_by = kwargs.get('user')

        if is_new and self.create_login:
            if User.objects.filter(email=self.email).exists():
                raise ValueError("A user with this email already exists.")
            if not self.password:
                raise ValueError("Password is required when creating a login.")
            
            junior_group, created = Group.objects.get_or_create(name='junior')
            
            user = User.objects.create_user(
                username=self.email,
                email=self.email,
                password=self.password,
                first_name=self.name,
                is_active=self.allow_login
            )
            user.groups.add(junior_group)
            user.save()
            self.user = user
        elif not is_new and self.user:
            # Update existing user fields
            self.user.first_name = self.name
            self.user.email = self.email
            self.user.username = self.email
            self.user.is_active = self.allow_login
            if self.password:
                self.user.set_password(self.password)
            self.user.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Advocate"
        verbose_name_plural = "Advocates"

class AdvocateSnippetViewSet(SnippetViewSet):
    model = Advocate
    icon = 'user'
    add_to_admin_menu = True
    list_display = (
        'name', 'email', 'mobile_no', 'barcode_number', 'can_add_cases',
        'can_modify_cases', 'can_view_all_cases', 'can_view_assigned_cases',
        'can_view_case_fees', 'created_by', 'user', 'created_at'
    )
    list_export = (
        'name', 'email', 'mobile_no', 'barcode_number', 'can_add_cases',
        'can_modify_cases', 'can_view_all_cases', 'can_view_assigned_cases',
        'can_view_case_fees', 'created_by', 'user', 'created_at'
    )
    inspect_view_enabled = True
    list_filter = ('created_at', 'created_by', 'can_add_cases', 'can_modify_cases', 'can_view_all_cases')
    search_fields = ('name', 'email', 'mobile_no', 'barcode_number', 'created_by__username', 'user__username')

register_snippet(AdvocateSnippetViewSet)