from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment, PrivateMessage

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
            'bio',
            'profile_pic',
            'followers_count',
            'following_count',
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']


class PrivateMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    sender_pfp = serializers.SerializerMethodField()

    class Meta:
        model = PrivateMessage
        fields = [
            'id',
            'sender_id',
            'text',
            'sender_pfp',
            'created_at',
        ]

    def get_sender_pfp(self, obj):
        if obj.sender.profile_pic:
            return obj.sender.profile_pic.url
        return None