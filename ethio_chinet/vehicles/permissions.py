from rest_framework import permissions

class IsAdminUserCustom(permissions.BasePermission):
    """Allow only admin users to create/update/delete"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True  # allow everyone to view if needed
        return request.user.is_staff or request.user.user_type == 'admin'

class IsDriverUser(permissions.BasePermission):
    """Allow only drivers to create/update their own vehicle"""
    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.user_type == 'driver'
        return True
