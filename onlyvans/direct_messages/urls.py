from django.urls import path
from . import views

app_name = 'direct_messages'
urlpatterns = [
    path('', views.direct_messages, name='direct_messages'),
    path('send/<str:username>/', views.view_thread, name='view_thread_with_user'),
    path('thread/<int:thread_id>/', views.view_thread, name='view_thread'),
]