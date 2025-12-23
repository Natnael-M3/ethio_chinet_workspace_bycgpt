# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from .models import User


# class TokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         token = request.headers.get('Authorization')

#         if not token:
#             return None  # allow unauthenticated access if view allows

#         try:
#             user = User.objects.get(auth_token=token)
#         except User.DoesNotExist:
#             raise AuthenticationFailed('Invalid or expired token')

#         if user.status != 'active':
#             raise AuthenticationFailed('User is suspended')

#         return (user, None)

