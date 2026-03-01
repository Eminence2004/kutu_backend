from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Post, PrivateMessage, Comment
from .serializers import (
    CommentSerializer, UserSerializer, PrivateMessageSerializer
)

User = get_user_model()

# --- AUTH VIEWS ---
class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password')
        full_name = request.data.get('full_name')
        username = request.data.get('username', '').strip()
        student_id = request.data.get('student_id')
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username taken."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.create_user(email=email, password=password, full_name=full_name, username=username, student_id=student_id)
            return Response({"message": "Account created!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "user_id": user.id,
                "username": user.username,
                "profile_pic": user.profile_pic.url if user.profile_pic else None
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# --- VIBE FEED ---
class PostView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        posts = Post.objects.filter(user_id=user_id) if user_id else Post.objects.all()
        posts = posts.order_by('-created_at')
        data = [{
            "id": p.id, "user": p.user.username, "user_id": p.user.id,
            "image": p.image.url if p.image else None, "caption": p.caption,
            "likes_count": p.likes.count(), "is_liked_by_me": p.likes.filter(id=request.user.id).exists()
        } for p in posts]
        return Response(data)

    def post(self, request):
        Post.objects.create(user=request.user, image=request.data.get('image'), caption=request.data.get('caption', ''))
        return Response({"message": "Vibe posted!"}, status=status.HTTP_201_CREATED)

class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            return Response({"status": "unliked"})
        post.likes.add(request.user)
        return Response({"status": "liked"})

# --- COMMENT VIEW ---
class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(user=request.user, post=post, text=text)
        return Response({"status": "commented"}, status=status.HTTP_201_CREATED)

# --- SOCIAL ---
class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.query_params.get('q', '')
        users = User.objects.filter(Q(full_name__icontains=query) | Q(username__icontains=query)).exclude(id=request.user.id)
        return Response(UserSerializer(users[:10], many=True).data)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_following = request.user.following.filter(id=pk).exists()
        data = UserSerializer(user).data
        data['is_following'] = is_following
        data['followers_count'] = user.followers.count()
        data['following_count'] = user.following.count()
        return Response(data)

class ToggleFollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user: 
            return Response({"error": "Cannot follow self"}, status=400)
        
        if request.user.following.filter(id=user_id).exists():
            request.user.following.remove(target_user)
            is_following = False
        else:
            request.user.following.add(target_user)
            is_following = True
            
        return Response({
            "is_following": is_following,
            "followers_count": target_user.followers.count()
        })

# --- CHAT ---
class PrivateChatView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, receiver_id):
        messages = PrivateMessage.objects.filter(
            (Q(sender=request.user, receiver_id=receiver_id)) |
            (Q(sender_id=receiver_id, receiver=request.user))
        ).order_by('created_at')
        return Response(PrivateMessageSerializer(messages, many=True).data)

    def post(self, request, receiver_id):
        text = request.data.get('text')
        if not text: return Response({"error": "Empty message"}, status=400)
        msg = PrivateMessage.objects.create(sender=request.user, receiver_id=receiver_id, text=text)
        return Response(PrivateMessageSerializer(msg).data, status=201)

class ChatListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        msgs = PrivateMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        u_ids = set()
        for m in msgs:
            u_ids.add(m.sender_id if m.sender_id != request.user.id else m.receiver_id)
        users = User.objects.filter(id__in=u_ids)
        data = []
        for u in users:
            try:
                last = PrivateMessage.objects.filter(Q(sender=request.user, receiver=u) | Q(sender=u, receiver=request.user)).latest('created_at')
                last_text = last.text[:30]
            except PrivateMessage.DoesNotExist:
                last_text = ""
            
            data.append({
                "id": u.id, "full_name": u.full_name, "username": u.username,
                "profile_pic": u.profile_pic.url if u.profile_pic else None,
                "last_message": last_text
            })
        return Response(data)

# --- PROFILE & USER POSTS ---
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = UserSerializer(request.user).data
        data['followers_count'] = request.user.followers.count()
        data['following_count'] = request.user.following.count()
        return Response(data)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request):
        user = request.user
        if 'profile_pic' in request.data:
            user.profile_pic = request.data['profile_pic']
        if 'bio' in request.data:
            user.bio = request.data['bio']
        user.save()
        return Response(UserSerializer(user).data)

class UserPostView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        data = [{
            "id": p.id, 
            "image": p.image.url if p.image else None, 
            "caption": p.caption
        } for p in posts]
        return Response(data)