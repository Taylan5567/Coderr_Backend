from rest_framework.permissions import BasePermission

class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.type == 'business'