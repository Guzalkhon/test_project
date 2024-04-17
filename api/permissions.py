from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsAuthorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        
        if view.action == 'like_toggle':
            return True
        
        if view.action == 'save_toggle':
            return True

        return request.user == obj.author


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.author.id or request.user.is_staff
