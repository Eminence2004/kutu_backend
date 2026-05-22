from django.urls import path
from .views import (
    SignupView, LoginView, PostView, 
    UserSearchView, PrivateChatView, UserDetailView, 
    ChatListView, ToggleLikeView, ToggleFollowView, 
    CommentView, ProfileView, UserPostView,
    ProfileUpdateView  # Added this import
)

urlpatterns = [
    # Auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    
    # Profile Logic
    path('auth/profile/', ProfileView.as_view(), name='user-profile'),
    path('auth/profile/update/', ProfileUpdateView.as_view(), name='profile-update'), # New path for image uploads

    # Feed & User Content
    path('posts/', PostView.as_view(), name='posts'),
    path('posts/mine/', UserPostView.as_view(), name='my-posts'), 
    path('posts/<int:post_id>/like/', ToggleLikeView.as_view(), name='like-post'),
    path('posts/<int:post_id>/comments/', CommentView.as_view(), name='post-comments'),
    
    # Social
    path('search-users/', UserSearchView.as_view(), name='user-search'),
    path('users-detail/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),

    # Private Messaging
    path('chat-list/', ChatListView.as_view(), name='chat-list'),
    path('private-chat/<int:receiver_id>/', PrivateChatView.as_view(), name='private-chat'),
]