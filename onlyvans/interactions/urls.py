from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.direct_messages, name='direct_messages'),
    path('messages/send/<str:username>/', views.view_thread, name='view_thread_with_user'),
    path('messages/thread/<int:thread_id>/', views.view_thread, name='view_thread'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
]

"""
URL configuration for the interactions application.

Each path function specifies a URL pattern and the view that should handle
requests to that pattern. Additionally, a name is provided for each URL pattern
to make it easier to refer to them in templates and other parts of the application.

Paths:
- 'messages/': Displays direct messages for the logged-in user. View: views.direct_messages
- 'messages/send/<str:username>/': Displays a message thread with a specific user. View: views.view_thread
- 'messages/thread/<int:thread_id>/': Displays a specific message thread by thread ID. View: views.view_thread
- 'like/<int:post_id>/': Allows the logged-in user to like a specific post. View: views.like_post
"""
