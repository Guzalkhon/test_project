from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.viewsets import mixins
from rest_framework import permissions
from rest_framework.response import Response

from .permissions import *
from .models import *
from .serializers import *


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAdminUser
    ]

    @action(detail=True, methods=['PUT'])
    def add_remove_manager(self, request, pk=None):
        if request.user.is_authenticated and request.user.is_superuser:
            if not User.objects.filter(pk=pk).exists():
                return Response({'error': 'User does not exist'})
            
            user = User.objects.get(pk=pk)

            if user.is_staff:
                user.is_staff = False
                return Response({
                    'success': 'User removed from manager list',
                    'is_staff': False
                })
            
            user.is_staff = True
            return Response({
                'success': 'User added to manager list',
                'is_staff': True
            })
        return Response({'error': 'Access is not allowed'})


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created')
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
    

    @action(detail=True, methods=['POST'])
    def like_toggle(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'You must be logged in to like a post'}, status=404)
        
        if not Post.objects.filter(pk=pk).exists():
            return Response({'error': 'Post does not exist'}, status=404)
        
        post = self.get_object()

        if request.user == post.author:
            return Response({'error': 'You cannot like your own post'}, status=404)

        if request.user in post.liked_by.all():
            post.liked_by.remove(request.user)
            return Response({
                'success': 'Post unliked successfully',
                'liked': False,
                'likes_count': post.liked_by.count()
            })

        post.liked_by.add(request.user)
        return Response({
            'success': 'Post liked successfully',
            'liked': True,
            'likes_count': post.liked_by.count()
        })
    
    @action(detail=True, methods=['GET'])
    def get_by_id(self, request, pk=None):
        if not Post.objects.filter(pk=pk).exists():
            return Response({'error': 'Post does not exist'}, status=404)
        
        return self.get_object()
    
    
    @action(detail=True, methods=['POST'])
    def save_toggle(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'You must be logged in to like a post'}, status=404)
        
        if not Post.objects.filter(pk=pk).exists():
            return Response({'error': 'Post does not exist'}, status=404)
        
        post = self.get_object()

        if request.user == post.author:
            return Response({'error': 'You cannot save your own post'}, status=404)
        
        if request.user in post.saved_by.all():
            post.saved_by.remove(request.user)
            return Response({
                'success': 'Post deleted from saved successfully',
                'saved': False,
                'saves_count': post.saved_by.count()
            })

        post.saved_by.add(request.user)
        return Response({
            'success': 'Post saved successfully',
            'saved': True,
            'saves_count': post.saved_by.count()
        })
    
    @action(detail=False, methods=['GET'])
    def saved_posts(self, request):
        posts = Post.objects.filter(saved_by__id=request.user.id)
        return Response(PostSerializer(posts, many=True).data, status=200)
    

    @action(detail=True, methods=['GET'])
    def get_comment_by_post_id(self, request, pk=None):
        if not Post.objects.filter(pk=pk).exists():
            return Response({'error': 'Post does not exist'}, status=404)
        
        post = Post.objects.get(pk=pk)
        
        comments = post.comments.all().order_by('-created')

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        if not Post.objects.filter(pk=pk).exists():
            return Response({'error': 'Post does not exist'}, status=404)
        if IsAuthor:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'error': 'Permission not found'}, status=403)
        
    def update(self, request, pk=None, *args, **kwargs):
        if not Post.objects.filter(pk=pk).exists():
            return Response({'error': 'Post does not exist'}, status=404)
        if IsAuthor:
            return super().update(request, *args, **kwargs)
        else:
            return Response({'error': 'Permission not found'}, status=403)
        


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created')
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        if not Comment.objects.filter(pk=pk).exists():
            return Response({'error': 'Comment does not exist'}, status=404)
        if IsAuthor:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'error': 'Permission not found'}, status=403)
    

@api_view(['POST'])
def register(request):
    register_serializer = RegisterSerializer(data=request.data)
    print(register_serializer.is_valid())

    if not register_serializer.is_valid():
        return Response({'error': 'User credentials are not valid'}, status=404)
    username = register_serializer.data['username']
    password = register_serializer.data['password']
    confirm_password = register_serializer.data['confirm_password']
    email = register_serializer.data['email']

    if password != confirm_password:
        return Response({'error': 'Password do not match.'})
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken'})
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already taken'})

    user = User.objects.create_user(username, email, password)
    user.save()

    return Response({'success': 'User created successfully.'})

