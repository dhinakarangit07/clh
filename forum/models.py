from django.db import models
from django.contrib.auth.models import User
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forum_profile')
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class ForumPost(models.Model):
    CATEGORY_CHOICES = [
        ('case law', 'Case Law'),
        ('legal updates', 'Legal Updates'),
        ('case discussion', 'Case Discussion'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_posts")
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    image = models.ImageField(upload_to='forum/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("user"),
        FieldPanel("title"),
        FieldPanel("content"),
        FieldPanel("category"),
        FieldPanel("image"),
    ]

    def __str__(self):
        return f"{self.user.username} - {self.title[:30]}"

    class Meta:
        verbose_name = "Forum Post"
        verbose_name_plural = "Forum Posts"

class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='forum/comments/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.title[:30]}"

    class Meta:
        verbose_name = "Forum Comment"
        verbose_name_plural = "Forum Comments"

class ForumLike(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.post.title[:30]}"

class ForumPostSnippetViewSet(SnippetViewSet):
    model = ForumPost
    icon = "doc-full-inverse"
    add_to_admin_menu = True
    list_display = ("user", "title", "category", "created_at")
    list_filter = ("user", "category")
    search_fields = ("title", "content")

register_snippet(ForumPostSnippetViewSet)