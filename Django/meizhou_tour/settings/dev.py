"""
开发环境配置
- DEBUG: True
- 数据库：本地 MySQL（meizhou/xingning/514500）
- CORS：允许全部跨域
"""
from .base import *  # noqa
from dotenv import dotenv_values

DEBUG = True

# 本地 MySQL 配置（小皮面板 meizhou），可通过 .env 覆盖
_env = dotenv_values(BASE_DIR / '.env')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _env.get('DB_NAME', 'meizhou'),
        'USER': _env.get('DB_USER', 'xingning'),
        'PASSWORD': _env.get('DB_PASSWORD', '514500'),
        'HOST': _env.get('DB_HOST', '127.0.0.1'),
        'PORT': _env.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 开发环境允许全部跨域
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
