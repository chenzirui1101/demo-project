from django.db import models
from django.contrib.auth.models import User


# 景点分类
class Category(models.Model):
    name = models.CharField('分类名称', max_length=50)
    icon = models.CharField('图标URL', max_length=500, blank=True)
    sort = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '景点分类'
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.name


# 景点
class Attraction(models.Model):
    name = models.CharField('景点名称', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='attractions', verbose_name='分类')
    cover = models.CharField('封面图URL', max_length=2000)
    images = models.TextField('图片URL列表(JSON)', blank=True, default='')
    description = models.TextField('景点介绍')
    location = models.CharField('位置', max_length=200, blank=True)
    longitude = models.FloatField('经度', null=True, blank=True)
    latitude = models.FloatField('纬度', null=True, blank=True)
    ticket_price = models.DecimalField('门票价格', max_digits=8, decimal_places=2, default=0)
    open_time = models.CharField('开放时间', max_length=100, blank=True)
    rating = models.FloatField('评分', default=5.0)
    view_count = models.IntegerField('浏览量', default=0)
    is_hot = models.BooleanField('热门推荐', default=False)
    is_recommended = models.BooleanField('精选推荐', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '景点'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# 首页轮播图
class Banner(models.Model):
    title = models.CharField('标题', max_length=100)
    image = models.CharField('图片URL', max_length=2000)
    link_type = models.CharField('跳转类型', max_length=20, default='attraction')  # attraction / url
    attraction = models.ForeignKey(Attraction, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='关联景点')
    sort = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.title


# 用户资料扩展
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',
                                verbose_name='用户')
    nickname = models.CharField('昵称', max_length=50, blank=True)
    avatar = models.CharField('头像URL', max_length=500, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname or self.user.username


# 收藏
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites',
                             verbose_name='用户')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='favorited_by',
                                   verbose_name='景点')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'attraction')

    def __str__(self):
        return f'{self.user.username} - {self.attraction.name}'


# 评论
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews',
                             verbose_name='用户')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='reviews',
                                   verbose_name='景点')
    content = models.TextField('评论内容')
    rating = models.IntegerField('评分', default=5)
    created_at = models.DateTimeField('评论时间', auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}评论{self.attraction.name}'


# 浏览历史
class BrowsingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='browsing_history',
                             verbose_name='用户')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='viewed_by',
                                   verbose_name='景点')
    viewed_at = models.DateTimeField('浏览时间', auto_now_add=True)

    class Meta:
        verbose_name = '浏览历史'
        verbose_name_plural = verbose_name
        ordering = ['-viewed_at']
        # 同一用户+同一景点只保留最新一条，避免重复记录
        unique_together = ('user', 'attraction')

    def __str__(self):
        return f'{self.user.username}浏览{self.attraction.name}'


# API Token（用于小程序等不支持cookie的客户端）
class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='api_token',
                                verbose_name='用户')
    token = models.CharField('Token', max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = 'API Token'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} - {self.token[:8]}...'
