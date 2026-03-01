from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User, Post, ChatMessage, PrivateMessage, Follow, Comment

@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    list_display = ('email', 'full_name', 'username', 'student_id', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'student_id', 'username')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)

@admin.register(Post)
class PostAdmin(ModelAdmin):
    # FIX: Uses 'created_at' and a custom method for likes
    list_display = ('user', 'caption', 'created_at', 'get_likes_count')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = "Likes ❤️"

@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    # FIX: Changed 'message' to 'text' and 'timestamp' to 'created_at'
    list_display = ('user', 'text', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__full_name')

@admin.register(PrivateMessage)
class PrivateMessageAdmin(ModelAdmin):
    # FIX: Changed 'recipient' to 'receiver' and 'timestamp' to 'created_at'
    list_display = ('sender', 'receiver', 'text', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__full_name', 'receiver__full_name', 'text')

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'post', 'text', 'created_at')
    list_filter = ('created_at',)

@admin.register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('user_from', 'user_to', 'created')