from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User, Post, ChatMessage, PrivateMessage, Follow, Comment


@admin.register(User)
class CustomUserAdmin(ModelAdmin, BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('email', 'full_name', 'username', 'student_id', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'student_id', 'username')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'username', 'student_id', 'profile_pic', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'student_id', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('user', 'caption', 'created_at', 'get_likes_count')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    search_fields = ('user__email', 'user__full_name', 'caption')

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = "Likes ❤️"


@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ('user', 'text', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__full_name')
    readonly_fields = ('created_at',)


@admin.register(PrivateMessage)
class PrivateMessageAdmin(ModelAdmin):
    list_display = ('sender', 'receiver', 'text', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__full_name', 'receiver__full_name', 'text')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'post', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__full_name', 'text')
    readonly_fields = ('created_at',)


@admin.register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('user_from', 'user_to', 'created')
    search_fields = ('user_from__full_name', 'user_to__full_name')
    readonly_fields = ('created',)