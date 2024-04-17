from api.models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    likes = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    comments = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = User
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    liked_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    saved_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created', 'updated', 'liked_by', 'saved_by']
        read_only_fields = ['created', 'updated', 'liked_by', 'saved_by']

    def create(self, validated_data):
        return Post.objects.create(author=self.context['request'].user, **validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    confirm_password = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content = serializers.CharField()

    class Meta:
        models = Comment
        fields = '__all__'
        read_only_fields = ['created', 'updated']

