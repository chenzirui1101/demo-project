import os
import json
from django.contrib import admin
from django import forms
from django.conf import settings
from .models import (
    Category, Attraction, Banner, UserProfile,
    Favorite, Review, BrowsingHistory,
)


class AttractionAdminForm(forms.ModelForm):
    """景点表单：支持上传封面图和多张详情图到本地 media 文件夹"""
    cover_upload = forms.ImageField(
        required=False, label='上传封面图（保存到本地 media/attractions/）',
        help_text='上传后自动覆盖封面图URL。留空则保持原有在线图片URL。',
    )
    images_upload = forms.FileField(
        required=False, label='上传详情图（可多选，保存到本地）',
        help_text='按住Ctrl多选图片，上传后追加到图片列表。留空则保持原有。',
    )

    class Meta:
        model = Attraction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            cover = self.instance.cover or ''
            if cover.startswith('/media/'):
                self.fields['cover_upload'].help_text = f'当前已使用本地上传图: {cover}。重新上传将覆盖。'
            elif cover:
                self.fields['cover_upload'].help_text = f'当前使用在线图片。上传新图将替换为本地路径。'

    def _save_upload(self, uploaded_file, subdir='attractions'):
        """保存上传文件到 media 子目录，返回相对URL路径"""
        upload_dir = os.path.join(settings.MEDIA_ROOT, subdir)
        os.makedirs(upload_dir, exist_ok=True)
        # 安全文件名：只保留字母数字和中文，替换空格
        import re
        safe_name = re.sub(r'[^\w\u4e00-\u9fa5.-]', '_', uploaded_file.name)
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
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        return f'/media/{subdir}/{safe_name}'

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 处理封面图上传
        cover_file = self.cleaned_data.get('cover_upload')
        if cover_file:
            instance.cover = self._save_upload(cover_file, 'attractions/covers')
        # 处理详情图多文件上传
        images_file = self.cleaned_data.get('images_upload')
        if images_file:
            existing = []
            if instance.images:
                try:
                    existing = json.loads(instance.images)
                except (json.JSONDecodeError, TypeError):
                    existing = []
            # FileField 单个文件，但 forms.FileField 也能拿到文件对象
            url = self._save_upload(images_file, 'attractions/details')
            existing.append(url)
            instance.images = json.dumps(existing, ensure_ascii=False)
        if commit:
            instance.save()
        return instance


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sort')
    list_editable = ('name', 'sort')


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    form = AttractionAdminForm
    list_display = ('id', 'name', 'category', 'rating', 'view_count', 'is_hot', 'is_recommended')
    list_filter = ('category', 'is_hot', 'is_recommended')
    search_fields = ('name', 'description')
    list_editable = ('rating', 'is_hot', 'is_recommended')
    # cover 字段保持可编辑（支持直接粘贴在线URL）
    readonly_fields = ('view_count',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sort', 'is_active')
    list_editable = ('title', 'sort', 'is_active')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nickname', 'phone')
    search_fields = ('user__username', 'nickname')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'attraction', 'created_at')
    list_filter = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'attraction', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('content',)


@admin.register(BrowsingHistory)
class BrowsingHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'attraction', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__username', 'attraction__name')
