from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.direct_messages, name='direct_messages'),
    path('messages/send/<str:username>/', views.view_thread, name='view_thread_with_user'),
    path('messages/thread/<int:thread_id>/', views.view_thread, name='view_thread'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
]