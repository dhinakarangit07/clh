from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ForumPost, ForumComment, ForumLike, Profile
from wagtail.images.models import Image
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

class ProfileSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'photo']

    def get_photo(self, obj):
        if obj.photo:
            request = self.context.get('request')
            try:
                rendition = obj.photo.get_rendition('max-200x200')
                photo_url = request.build_absolute_uri(rendition.url) if request else rendition.url
                return photo_url
            except Exception:
                return None
        return None

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

    def get_profile(self, obj):
        try:
            profile = obj.profile
            return ProfileSerializer(profile, context=self.context).data
        except Profile.DoesNotExist:
            return {
                'first_name': obj.first_name or '',
                'last_name': obj.last_name or '',
                'photo': None
            }

class ForumCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ForumComment
        fields = ['id', 'post_id', 'user', 'content', 'image_url', 'created_at']
        read_only_fields = ['id', 'user', 'image_url', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        post_id = validated_data.pop('post_id')
        post = ForumPost.objects.get(id=post_id)
        return ForumComment.objects.create(post=post, user=self.context['request'].user, **validated_data)

class ForumPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = ForumCommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ForumPost
        fields = [
            'id', 'user', 'title', 'content', 'category', 'image', 'image_url',
            'created_at', 'updated_at', 'likes_count', 'liked_by_user', 'comment_count', 'comments'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at', 'likes_count',
            'liked_by_user', 'comment_count', 'comments', 'image_url'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

from rest_framework import generics, permissions, status, pagination
from rest_framework.response import Response

class ForumPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class ForumPostListCreateView(generics.ListCreateAPIView):
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ForumPagination

    def get_serializer_context(self):
        return super().get_serializer_context()

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        return queryset

    def perform_create(self, serializer):
        print("Request files:", self.request.FILES)  # Debug: Check if image is received
        instance = serializer.save(user=self.request.user)
        print("Saved instance image:", instance.image)  # Debug: Check saved image

class ForumCommentCreateView(generics.CreateAPIView):
    serializer_class = ForumCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return super().get_serializer_context()

class ForumLikeToggleView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = ForumPost.objects.get(pk=post_id)
        except ForumPost.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        like, created = ForumLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'message': 'Unliked'}, status=status.HTTP_200_OK)
        return Response({'message': 'Liked'}, status=status.HTTP_201_CREATED)

class MyFeedView(generics.ListAPIView):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ForumPagination

    def get_serializer_context(self):
        return super().get_serializer_context()

    def get_queryset(self):
        return ForumPost.objects.filter(user=self.request.user).order_by('-created_at')

class AllFeedView(generics.ListAPIView):
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ForumPagination

    def get_serializer_context(self):
        return super().get_serializer_context()

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        return queryset

class UserLikedPostsView(generics.ListAPIView):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ForumPagination

    def get_serializer_context(self):
        return super().get_serializer_context()

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return ForumPost.objects.none()

        liked_post_ids = ForumLike.objects.filter(user=user).values_list('post_id', flat=True)
        return ForumPost.objects.filter(id__in=liked_post_ids).order_by('-created_at')

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"csrfToken": request.META.get("CSRF_COOKIE", "")})