from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),

    # Posts
    path('posts/', views.PostView.as_view(), name='posts'),
    path('posts/mine/', views.UserPostView.as_view(), name='my-posts'),
    path('posts/<int:post_id>/like/', views.ToggleLikeView.as_view(), name='toggle-like'),
    path('posts/<int:post_id>/delete/', views.DeletePostView.as_view(), name='delete-post'),
    path('posts/<int:post_id>/comments/', views.CommentView.as_view(), name='comments'),

    # Social
    path('users/search/', views.UserSearchView.as_view(), name='user-search'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/follow/', views.ToggleFollowView.as_view(), name='toggle-follow'),

    # Chat
    path('chat/', views.ChatListView.as_view(), name='chat-list'),
    path('chat/<int:receiver_id>/', views.PrivateChatView.as_view(), name='private-chat'),

    # ID Card Finder (Item 1)
    path('find-student/', views.find_student, name='find-student'),
    path('contact-request/send/', views.send_contact_request, name='send-contact-request'),
    path('contact-request/inbox/', views.get_contact_requests, name='contact-request-inbox'),
    path('contact-request/respond/', views.respond_contact_request, name='respond-contact-request'),
]