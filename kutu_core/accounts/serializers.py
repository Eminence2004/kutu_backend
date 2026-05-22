from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment, PrivateMessage, Post

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'student_id',
            'bio',
            'profile_pic',
            'followers_count',
            'following_count',
        ]


class PostAuthorSerializer(serializers.ModelSerializer):
    """Lightweight user info embedded inside each post."""
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile_pic_url']

    def get_profile_pic_url(self, obj):
        request = self.context.get('request')
        if obj.profile_pic:
            url = obj.profile_pic.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_info = PostAuthorSerializer(source='user', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_info', 'image', 'caption', 'created_at', 'likes_count']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']


class PrivateMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_pfp = serializers.SerializerMethodField()

    class Meta:
        model = PrivateMessage
        fields = ['id', 'sender_id', 'text', 'sender_pfp', 'created_at']

    def get_sender_pfp(self, obj):
        request = self.context.get('request')
        if obj.sender.profile_pic:
            url = obj.sender.profile_pic.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None