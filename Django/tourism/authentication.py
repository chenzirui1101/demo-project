from rest_framework import authentication, exceptions
from django.utils import timezone
from .models import UserToken
import uuid


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    """
    跳过 CSRF 校验的 SessionAuthentication。
    前端通过 Vite 代理调用 API，无法携带 CSRF token，
    因此对 API 请求关闭 CSRF 强制校验，仅依赖 session cookie 认证。
    """

    def enforce_csrf(self, request):
        return


class TokenAuthentication(authentication.BaseAuthentication):
    """
    基于 Authorization: Token <token> 的认证方式。
    用于微信小程序等不支持 cookie 的客户端。
    """

    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token_string = parts[1]
        try:
            token_obj = UserToken.objects.select_related('user').get(token=token_string)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token无效')

        if not token_obj.user.is_active:
            raise exceptions.AuthenticationFailed('用户已被禁用')

        return (token_obj.user, token_obj)

    def authenticate_header(self, request):
        return self.keyword
