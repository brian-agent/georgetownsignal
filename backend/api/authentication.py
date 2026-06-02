"""
api/authentication.py

Validates Supabase JWT tokens on every authenticated request.
No Django sessions. No Django users for vendors.
The JWT payload contains: sub (= supabase_uid), email, role.
"""
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SupabaseUser:
    """Lightweight user object injected into request.user from JWT claims."""

    def __init__(self, payload: dict):
        self.supabase_uid: str = payload.get('sub', '')
        self.email: str        = payload.get('email', '')
        self.role: str         = payload.get('role', 'authenticated')
        self.is_authenticated  = True
        self.is_anonymous      = False

    def __str__(self):
        return self.email


class SupabaseJWTAuthentication(BaseAuthentication):
    """
    Reads Authorization: Bearer <supabase_jwt>
    Verifies signature with SUPABASE_JWT_SECRET.
    Sets request.user to a SupabaseUser instance.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return None

        secret = settings.SUPABASE_JWT_SECRET
        if not secret:
            raise AuthenticationFailed('SUPABASE_JWT_SECRET not configured')

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=['HS256'],
                options={'verify_exp': True},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {e}')

        return (SupabaseUser(payload), token)

    def authenticate_header(self, request):
        return 'Bearer realm="georgetownsignal"'
