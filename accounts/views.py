from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import Post, PrivateMessage, Comment, ContactRequest
from .serializers import CommentSerializer, UserSerializer, PrivateMessageSerializer

User = get_user_model()


# --- AUTH VIEWS ---
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password')
        full_name = request.data.get('full_name', '').strip()
        username = request.data.get('username', '').strip()
        student_id = request.data.get('student_id', '').strip()
        index_number = request.data.get('index_number', '').strip()
        phone_number = request.data.get('phone_number', '').strip()

        # --- Validations ---
        if not email or not password or not full_name:
            return Response({"error": "Email, password, and full name are required."}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=400)
        if username and User.objects.filter(username=username).exists():
            return Response({"error": "Username taken."}, status=400)
        if student_id and User.objects.filter(student_id=student_id).exists():
            return Response({"error": "Student ID already registered."}, status=400)
        if index_number and User.objects.filter(index_number=index_number).exists():
            return Response({"error": "Index number already registered."}, status=400)

        try:
            User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                username=username or None,
                student_id=student_id or None,
                index_number=index_number or None,
                phone_number=phone_number or None,
            )
            return Response({"message": "Account created!"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


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
                "refresh": str(refresh),
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "profile_pic": user.profile_pic.url if user.profile_pic else None,
            })
        return Response({"error": "Invalid credentials"}, status=401)


# --- VIBE FEED ---
class PostView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        posts = Post.objects.filter(user_id=user_id) if user_id else Post.objects.all()
        posts = posts.order_by('-created_at')
        data = [{
            "id": p.id,
            "user": p.user.username,
            "user_id": p.user.id,
            "full_name": p.user.full_name,
            "profile_pic": request.build_absolute_uri(p.user.profile_pic.url) if p.user.profile_pic else None,
            "image": request.build_absolute_uri(p.image.url) if p.image else None,
            "caption": p.caption,
            "created_at": p.created_at,
            "likes_count": p.likes.count(),
            "is_liked_by_me": p.likes.filter(id=request.user.id).exists(),
        } for p in posts]
        return Response(data)

    def post(self, request):
        image = request.data.get('image')
        if not image:
            return Response({"error": "Image is required."}, status=400)
        Post.objects.create(
            user=request.user,
            image=image,
            caption=request.data.get('caption', '')
        )
        return Response({"message": "Vibe posted!"}, status=201)


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
        return Response(CommentSerializer(comments, many=True).data)

    def post(self, request, post_id):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"error": "No text provided"}, status=400)
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(user=request.user, post=post, text=text)
        return Response({"status": "commented"}, status=201)


# --- SOCIAL ---
class UserSearchView(APIView):
    """Search users by username, full name, email, student_id, or index_number."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([])
        users = User.objects.filter(
            Q(full_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(student_id__iexact=query) |
            Q(index_number__iexact=query)
        ).exclude(id=request.user.id)
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
            return Response({"error": "Cannot follow yourself"}, status=400)
        if request.user.following.filter(id=user_id).exists():
            request.user.following.remove(target_user)
            is_following = False
        else:
            request.user.following.add(target_user)
            is_following = True
        return Response({
            "is_following": is_following,
            "followers_count": target_user.followers.count(),
        })


# --- CHAT ---
class PrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, receiver_id):
        messages = PrivateMessage.objects.filter(
            Q(sender=request.user, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver=request.user)
        ).order_by('created_at')
        return Response(PrivateMessageSerializer(messages, many=True).data)

    def post(self, request, receiver_id):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"error": "Empty message"}, status=400)
        msg = PrivateMessage.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            text=text
        )
        return Response(PrivateMessageSerializer(msg).data, status=201)


class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        msgs = PrivateMessage.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        )
        u_ids = set()
        for m in msgs:
            other_id = m.sender_id if m.sender_id != request.user.id else m.receiver_id
            u_ids.add(other_id)

        users = User.objects.filter(id__in=u_ids)
        data = []
        for u in users:
            try:
                last = PrivateMessage.objects.filter(
                    Q(sender=request.user, receiver=u) |
                    Q(sender=u, receiver=request.user)
                ).latest('created_at')
                last_text = last.text[:30]
            except PrivateMessage.DoesNotExist:
                last_text = ""

            data.append({
                "id": u.id,
                "full_name": u.full_name,
                "username": u.username,
                "profile_pic": u.profile_pic.url if u.profile_pic else None,
                "last_message": last_text,
            })
        return Response(data)


# --- PROFILE ---
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
        if 'phone_number' in request.data:
            user.phone_number = request.data['phone_number']
        user.save()
        return Response(UserSerializer(user).data)


class UserPostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        data = [{
            "id": p.id,
            "image": p.image.url if p.image else None,
            "caption": p.caption,
        } for p in posts]
        return Response(data)


# ─────────────────────────────────────────────
# ITEM 1: ID CARD FINDER — Find student by index number
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_student(request):
    """
    Search by index_number or student_id (printed on ID cards).
    Returns basic info so the finder can contact the owner.
    Does NOT expose phone number directly — they must send a contact request.
    Usage: GET /api/find-student/?q=2021CS0012
    """
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({"error": "Provide a student index number or ID."}, status=400)

    try:
        student = User.objects.get(
            Q(index_number__iexact=query) | Q(student_id__iexact=query)
        )
    except User.DoesNotExist:
        return Response({"error": "No student found with that ID."}, status=404)
    except User.MultipleObjectsReturned:
        # Shouldn't happen due to unique constraints but handle gracefully
        student = User.objects.filter(
            Q(index_number__iexact=query) | Q(student_id__iexact=query)
        ).first()

    return Response({
        "id": student.id,
        "full_name": student.full_name,
        "username": student.username,
        "profile_pic": request.build_absolute_uri(student.profile_pic.url) if student.profile_pic else None,
        # Phone only revealed after accepted contact request (see below)
        "phone_revealed": False,
    })


# ─────────────────────────────────────────────
# CONTACT REQUEST SYSTEM (for ID card finder)
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_contact_request(request):
    """
    After finding a student, send them a contact request.
    Body: { "student_id": "2021CS0012" }  OR  { "user_id": 5 }
    """
    # Support lookup by user_id (from find_student result) or student_id
    user_id = request.data.get('user_id')
    student_id_query = request.data.get('student_id', '').strip()

    if user_id:
        target = get_object_or_404(User, id=user_id)
    elif student_id_query:
        target = get_object_or_404(
            User,
            Q(student_id__iexact=student_id_query) | Q(index_number__iexact=student_id_query)
        )
    else:
        return Response({"error": "Provide user_id or student_id."}, status=400)

    if request.user == target:
        return Response({"error": "You cannot contact yourself."}, status=400)

    if ContactRequest.objects.filter(sender=request.user, receiver=target, status='pending').exists():
        return Response({"message": "Request already sent."})

    ContactRequest.objects.create(sender=request.user, receiver=target)
    return Response({"message": "Contact request sent."}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contact_requests(request):
    """List all pending contact requests received by the logged-in user."""
    requests_qs = ContactRequest.objects.filter(
        receiver=request.user, status='pending'
    ).select_related('sender')

    data = [{
        "id": r.id,
        "sender_id": r.sender.id,
        "sender_name": r.sender.full_name,
        "sender_username": r.sender.username,
        "sender_profile_pic": request.build_absolute_uri(r.sender.profile_pic.url) if r.sender.profile_pic else None,
        "created_at": r.created_at,
    } for r in requests_qs]

    return Response({"requests": data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_contact_request(request):
    """
    Accept or reject a contact request.
    Body: { "request_id": 3, "action": "accept" }
    On accept, the sender's phone number is revealed.
    """
    request_id = request.data.get('request_id')
    action = request.data.get('action')

    if action not in ('accept', 'reject'):
        return Response({"error": "Action must be 'accept' or 'reject'."}, status=400)

    req = get_object_or_404(ContactRequest, id=request_id, receiver=request.user)

    req.status = action + 'ed'  # 'accepted' or 'rejected'
    req.save()

    if action == 'accept':
        return Response({
            "message": "Request accepted.",
            "sender_name": req.sender.full_name,
            "phone_number": req.sender.phone_number or "Not provided",
        })

    return Response({"message": "Request rejected."})