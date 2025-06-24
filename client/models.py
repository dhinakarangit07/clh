# models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

class Client(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False, help_text="Enter client name")
    email = models.EmailField(blank=False, null=False, help_text="Enter email address")
    password = models.CharField(max_length=128, blank=True, null=True, help_text="Enter password for client login (if applicable)")
    create_login = models.BooleanField(default=False, help_text="Check to create a user account for this client")
    allow_login = models.BooleanField(default=True, help_text="Check to allow this client to log in (controls user active state)")
    contact_number = models.CharField(max_length=20, blank=True, null=True, help_text="Enter contact number")
    address = models.TextField(blank=True, null=True, help_text="Enter address")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select the user who created this client",
        related_name="clients_created"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The user account associated with this client",
        related_name="client_profile"
    )
    is_corporate = models.BooleanField(default=False, help_text="Check if this client is a corporate entity")
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        help_text="Total payment amount for the client"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("password"),
        FieldPanel("create_login"),
        FieldPanel("allow_login"),
        FieldPanel("contact_number"),
        FieldPanel("address"),
        FieldPanel("created_by"),
        FieldPanel("user"),
        FieldPanel("is_corporate"),
        FieldPanel("payment_amount"),
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
            
            client_group, created = Group.objects.get_or_create(name='client')
            
            user = User.objects.create_user(
                username=self.email,
                email=self.email,
                password=self.password,
                first_name=self.name,
                is_active=self.allow_login
            )
            user.groups.add(client_group)
            user.save()
            self.user = user
        elif not is_new and self.user:
            # Update existing user fields
            self.user.first_name = self.name
            self.user.email = self.email
            self.user.username = self.email  # Update username to match email
            self.user.is_active = self.allow_login
            if self.password:
                self.user.set_password(self.password)
            self.user.save()

        super().save(*args, **kwargs)
        
        if Client.objects.count() > 50:
            oldest_client = Client.objects.order_by("created_at").first()
            if oldest_client:
                oldest_client.delete()
        
        if is_new:
            pass  # Placeholder for notification logic

    def delete(self, *args, **kwargs):
        # Delete the associated user if it exists
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

class ClientSnippetViewSet(SnippetViewSet):
    model = Client
    icon = 'user'
    add_to_admin_menu = True
    list_display = ('name', 'email', 'contact_number', 'create_login', 'allow_login', 'is_corporate', 'payment_amount', 'created_by', 'user', 'created_at')
    list_export = ('name', 'email', 'contact_number', 'create_login', 'allow_login', 'is_corporate', 'payment_amount', 'created_by', 'user', 'created_at')
    inspect_view_enabled = True
    list_filter = ('created_at', 'created_by', 'create_login', 'allow_login', 'is_corporate')
    search_fields = ('name', 'email', 'contact_number', 'created_by__username', 'user__username')

register_snippet(ClientSnippetViewSet)