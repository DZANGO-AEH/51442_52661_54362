from django.contrib import admin
from .models import Thread, Message, Like, Comment

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('participants__username',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('thread', 'sender', 'body', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('sender__username', 'body')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'liked_at')
    list_filter = ('liked_at',)
    search_fields = ('user__username', 'post__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'text', 'commented_at')
    list_filter = ('commented_at',)
    search_fields = ('user__username', 'post__title', 'text')