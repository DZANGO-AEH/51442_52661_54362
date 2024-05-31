from django.contrib import admin
from . models import Post, Media, Tier


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_price', 'user', 'message_permission')
    list_filter = ('message_permission',)
    search_fields = ('name', 'user__username')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_free', 'posted_at')
    list_filter = ('is_free', 'posted_at')
    search_fields = ('title', 'user__username')


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('post', 'file', 'type', 'tier')
    list_filter = ('type',)
    search_fields = ('post__title',)