"""
生产环境配置
- DEBUG: False
- 数据库：通过环境变量 DATABASE_URL 读取（或拆分为 DB_* 变量）
- CORS：限制为指定域名
- 部署时请替换 ALLOWED_HOSTS / CORS_ALLOWED_ORIGINS 为实际域名
"""
import os
from .base import *  # noqa

DEBUG = False

# 允许访问的主机，部署时替换为实际域名
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'api.yourdomain.com').split(',')

# 数据库：优先解析 DATABASE_URL，否则使用拆分变量
def _parse_database_url(url):
    """解析 postgres://user:pass@host:port/dbname 或 mysql://... 格式"""
    from urllib.parse import urlparse
    p = urlparse(url)
    return {
        'ENGINE': 'django.db.backends.mysql' if p.scheme.startswith('mysql') else 'django.db.backends.postgresql',
        'NAME': p.path.lstrip('/'),
        'USER': p.username or '',
        'PASSWORD': p.password or '',
        'HOST': p.hostname or '127.0.0.1',
        'PORT': str(p.port or 3306),
        'OPTIONS': {'charset': 'utf8mb4'},
    }

_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    DATABASES = {'default': _parse_database_url(_db_url)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'meizhou'),
            'USER': os.environ.get('DB_USER', 'xingning'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }

# 生产环境限制跨域来源，替换为前端实际域名
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'https://www.yourdomain.com,http://localhost:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# 生产安全设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
