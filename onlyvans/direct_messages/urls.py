from django.urls import path
from . import views

app_name = 'direct_messages'
urlpatterns = [
    path('', views.message_threads, name='message_threads'),
    path('send/<str:username>/', views.send_message, name='send_message'),
    path('thread/<int:thread_id>/', views.view_thread, name='view_thread'),
]