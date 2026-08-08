import json
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Attraction, Banner, UserProfile, Favorite, Review, BrowsingHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AttractionListSerializer(serializers.ModelSerializer):
    """景点列表用精简序列化"""
    category_name = serializers.CharField(source='category.name', read_only=True, default='')

    class Meta:
        model = Attraction
        fields = ['id', 'name', 'cover', 'category', 'category_name', 'description',
                  'location', 'ticket_price', 'open_time',
                  'rating', 'view_count', 'is_hot', 'is_recommended']


class AttractionDetailSerializer(serializers.ModelSerializer):
    """景点详情用完整序列化"""
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    image_list = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Attraction
        fields = ['id', 'name', 'cover', 'images', 'image_list', 'category', 'category_name',
                  'description', 'location', 'longitude', 'latitude', 'ticket_price',
                  'open_time', 'rating', 'view_count', 'is_hot', 'is_recommended', 'created_at',
                  'review_count']
        extra_kwargs = {
            'cover': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'category': {'required': False, 'allow_null': True},
            'images': {'required': False, 'allow_blank': True},
            'location': {'required': False, 'allow_blank': True},
            'open_time': {'required': False, 'allow_blank': True},
        }

    def get_image_list(self, obj):
        if not obj.images:
            return []
        try:
            return json.loads(obj.images)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_review_count(self, obj):
        return obj.reviews.count()


class BannerSerializer(serializers.ModelSerializer):
    attraction_id = serializers.IntegerField(source='attraction.id', read_only=True, default=None)

    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'link_type', 'attraction_id', 'sort', 'is_active']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'avatar', 'phone']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    nickname = serializers.CharField(source='profile.nickname', read_only=True, default='')
    avatar = serializers.CharField(source='profile.avatar', read_only=True, default='')

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'is_staff', 'profile']


class FavoriteSerializer(serializers.ModelSerializer):
    attraction = AttractionListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'attraction', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.profile.nickname', read_only=True, default='')
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.CharField(source='user.profile.avatar', read_only=True, default='')

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'nickname', 'avatar', 'attraction',
                  'content', 'rating', 'created_at']
        read_only_fields = ['user']


class BrowsingHistorySerializer(serializers.ModelSerializer):
    attraction = AttractionListSerializer(read_only=True)
    attraction_id = serializers.IntegerField(source='attraction.id', read_only=True)
    attraction_name = serializers.CharField(source='attraction.name', read_only=True)
    attraction_cover = serializers.CharField(source='attraction.cover', read_only=True)
    category_name = serializers.CharField(source='attraction.category.name', read_only=True, default='')
    location = serializers.CharField(source='attraction.location', read_only=True, default='')

    class Meta:
        model = BrowsingHistory
        fields = ['id', 'attraction', 'attraction_id', 'attraction_name',
                  'attraction_cover', 'category_name', 'location', 'viewed_at']
