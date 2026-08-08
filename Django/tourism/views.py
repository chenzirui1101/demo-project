import json
import os
import re
import uuid
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .models import Category, Attraction, Banner, UserProfile, Favorite, Review, BrowsingHistory, UserToken
from .serializers import (
    CategorySerializer, AttractionListSerializer, AttractionDetailSerializer,
    BannerSerializer, UserSerializer, FavoriteSerializer, ReviewSerializer,
    BrowsingHistorySerializer,
)


def api_response(code=0, msg='success', data=None):
    """统一响应格式"""
    return Response({'code': code, 'msg': msg, 'data': data})


def _get_or_create_token(user, refresh=False):
    """为用户生成或获取 API Token"""
    if refresh:
        UserToken.objects.filter(user=user).delete()
    token_string = uuid.uuid4().hex
    return UserToken.objects.create(user=user, token=token_string)


class IsAdminOrReadOnly(IsAuthenticated):
    """管理员才能写，所有人可读"""
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff


# 分类
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return api_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(msg='删除成功')


# 轮播图
class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return api_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(msg='删除成功')


# 景点
class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'hot', 'recommended']:
            return AttractionListSerializer
        return AttractionDetailSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        # 搜索
        keyword = request.query_params.get('keyword')
        if keyword:
            qs = qs.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
        # 分类筛选
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        # 排序
        sort = request.query_params.get('sort')
        if sort == 'hot':
            qs = qs.order_by('-view_count')
        elif sort == 'rating':
            qs = qs.order_by('-rating')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'results': serializer.data,
            }
            return api_response(data=paginated_data)
        serializer = self.get_serializer(qs, many=True)
        return api_response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return api_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(msg='删除成功')

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """热门景点"""
        qs = self.queryset.filter(is_hot=True)[:6]
        serializer = AttractionListSerializer(qs, many=True)
        return api_response(data=serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """精选推荐"""
        qs = self.queryset.filter(is_recommended=True)[:8]
        serializer = AttractionListSerializer(qs, many=True)
        return api_response(data=serializer.data)


# 评论
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        attraction_id = request.query_params.get('attraction')
        qs = self.get_queryset()
        if attraction_id:
            qs = qs.filter(attraction_id=attraction_id)
        serializer = self.get_serializer(qs, many=True)
        return api_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return api_response(code=401, msg='请先登录')
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return api_response(data=serializer.data)


# 收藏
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('attraction').filter(attraction__isnull=False)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return api_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        attraction_id = request.data.get('attraction')
        if not attraction_id:
            return api_response(code=1, msg='缺少景点ID')
        fav, created = Favorite.objects.get_or_create(
            user=request.user, attraction_id=attraction_id
        )
        if not created:
            return api_response(msg='已收藏过')
        serializer = self.get_serializer(fav)
        return api_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(msg='取消收藏成功')

    @action(detail=False, methods=['get'])
    def check(self, request):
        """检查是否已收藏，返回 is_favorite + favorite id"""
        attraction_id = request.query_params.get('attraction')
        fav = Favorite.objects.filter(user=request.user, attraction_id=attraction_id).first()
        return api_response(data={
            'is_favorite': fav is not None,
            'id': fav.id if fav else None,
        })

    @action(detail=False, methods=['delete'])
    def remove_by_attraction(self, request):
        """按景点ID取消收藏"""
        attraction_id = request.query_params.get('attraction') or request.data.get('attraction')
        if not attraction_id:
            return api_response(code=1, msg='缺少景点ID')
        deleted, _ = Favorite.objects.filter(user=request.user, attraction_id=attraction_id).delete()
        if deleted:
            return api_response(msg='取消收藏成功')
        return api_response(code=1, msg='未收藏该景点')


# 浏览历史
class BrowsingHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """获取当前用户的浏览历史列表"""
        qs = BrowsingHistory.objects.filter(user=request.user).select_related('attraction', 'attraction__category')
        serializer = BrowsingHistorySerializer(qs, many=True)
        return api_response(data=serializer.data)

    def create(self, request):
        """记录一次浏览（如果已存在则更新时间）"""
        attraction_id = request.data.get('attraction')
        if not attraction_id:
            return api_response(code=1, msg='缺少景点ID')
        obj, created = BrowsingHistory.objects.update_or_create(
            user=request.user,
            attraction_id=attraction_id,
            defaults={},
        )
        if not created:
            from django.utils import timezone
            obj.viewed_at = timezone.now()
            obj.save(update_fields=['viewed_at'])
        serializer = BrowsingHistorySerializer(obj)
        return api_response(data=serializer.data)

    @action(detail=False, methods=['post'])
    def batch_record(self, request):
        """批量记录浏览（用于详情页加载时触发）"""
        attraction_id = request.data.get('attraction')
        if not attraction_id:
            return api_response(code=1, msg='缺少景点ID')
        obj, created = BrowsingHistory.objects.update_or_create(
            user=request.user,
            attraction_id=attraction_id,
            defaults={},
        )
        if not created:
            from django.utils import timezone
            obj.viewed_at = timezone.now()
            obj.save(update_fields=['viewed_at'])
        return api_response(msg='记录成功')

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """清空浏览历史"""
        BrowsingHistory.objects.filter(user=request.user).delete()
        return api_response(msg='已清空')


# 用户注册登录
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname', '')
        if not username or not password:
            return api_response(code=1, msg='用户名和密码不能为空')
        if User.objects.filter(username=username).exists():
            return api_response(code=1, msg='用户名已存在')
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, nickname=nickname or username)
        # 注册后自动生成 token
        token_obj = _get_or_create_token(user)
        serializer = UserSerializer(user)
        data = serializer.data
        data['token'] = token_obj.token
        return api_response(data=data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return api_response(code=1, msg='用户名或密码错误')
        from django.contrib.auth import login
        login(request, user)
        # 生成或刷新 token（已存在则重建）
        token_obj = _get_or_create_token(user, refresh=True)
        serializer = UserSerializer(user)
        data = serializer.data
        data['token'] = token_obj.token
        return api_response(data=data)


class LogoutView(APIView):
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        # 删除 token（如果存在）
        if hasattr(request, 'user') and request.user.is_authenticated:
            UserToken.objects.filter(user=request.user).delete()
        return api_response(msg='退出成功')


class UserInfoView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return api_response(code=401, msg='请先登录')
        serializer = UserSerializer(request.user)
        data = serializer.data
        # 返回用户的 token（如果存在）
        try:
            token_obj = UserToken.objects.get(user=request.user)
            data['token'] = token_obj.token
        except UserToken.DoesNotExist:
            pass
        return api_response(data=data)

    def put(self, request):
        if not request.user.is_authenticated:
            return api_response(code=401, msg='请先登录')
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.nickname = request.data.get('nickname', profile.nickname)
        profile.avatar = request.data.get('avatar', profile.avatar)
        profile.phone = request.data.get('phone', profile.phone)
        profile.save()
        serializer = UserSerializer(user)
        data = serializer.data
        try:
            token_obj = UserToken.objects.get(user=request.user)
            data['token'] = token_obj.token
        except UserToken.DoesNotExist:
            pass
        return api_response(data=data)


# 管理员专用：图片上传
class MediaUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """管理员上传图片到本地 media 目录"""
        file = request.FILES.get('file')
        subdir = request.data.get('subdir', 'attractions')
        if not file:
            return api_response(code=1, msg='请上传文件')
        upload_dir = os.path.join(settings.MEDIA_ROOT, subdir)
        os.makedirs(upload_dir, exist_ok=True)
        # 安全文件名
        safe_name = re.sub(r'[^\w\u4e00-\u9fa5.-]', '_', file.name)
        filepath = os.path.join(upload_dir, safe_name)
        # 避免重名覆盖
        if os.path.exists(filepath):
            base, ext = os.path.splitext(safe_name)
            counter = 1
            while os.path.exists(filepath):
                safe_name = f'{base}_{counter}{ext}'
                filepath = os.path.join(upload_dir, safe_name)
                counter += 1
        with open(filepath, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        url = f'/media/{subdir}/{safe_name}'
        return api_response(data={'url': url, 'name': safe_name})


# 管理员统计
class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        stats = {
            'attractions': Attraction.objects.count(),
            'categories': Category.objects.count(),
            'banners': Banner.objects.filter(is_active=True).count(),
            'users': User.objects.count(),
            'favorites': Favorite.objects.count(),
            'reviews': Review.objects.count(),
        }
        return api_response(data=stats)
