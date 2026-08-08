from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BannerViewSet, AttractionViewSet, ReviewViewSet,
    FavoriteViewSet, BrowsingHistoryViewSet, RegisterView, LoginView, LogoutView, UserInfoView,
    MediaUploadView, AdminStatsView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'attractions', AttractionViewSet, basename='attraction')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'browsing-history', BrowsingHistoryViewSet, basename='browsing-history')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/user/', UserInfoView.as_view(), name='user-info'),
    # 管理员接口
    path('admin/upload/', MediaUploadView.as_view(), name='media-upload'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
]
