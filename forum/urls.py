from django.urls import path
from .views import *

urlpatterns = [
    path("api/posts/", ForumPostListCreateView.as_view(), name="forum-post-list-create"),
    path("api/comments/", ForumCommentCreateView.as_view(), name="forum-comment-create"),
    path("api/posts/<int:post_id>/like-toggle/", ForumLikeToggleView.as_view(), name="forum-like-toggle"),
    path("api/my-feed/", MyFeedView.as_view(), name="forum-my-feed"),
    path("api/all-feed/", AllFeedView.as_view(), name="forum-all-feed"),
    path("api/liked-posts/<int:user_id>/", UserLikedPostsView.as_view(), name="forum-liked-posts"),
    path("api/get-csrf-token/", get_csrf_token, name="get-csrf-token"),
]