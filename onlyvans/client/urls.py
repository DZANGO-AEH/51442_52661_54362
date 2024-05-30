from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('discover/', views.discover_creators, name='discover_creators'),
    path('subscribe/<str:username>/', views.select_tier, name='select-tier'),
    path('subscribe/<str:username>/<int:tier_id>/', views.subscribe_to_tier, name='subscribe-to-tier'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions/extend/<int:subscription_id>/', views.extend_subscription, name='extend_subscription'),
    path('subscriptions/cancel/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),
]

"""
URL configuration for the client application.

Paths:
- 'dashboard/': Displays the user's dashboard. View: views.dashboard
- 'discover/': Allows users to discover new creators. View: views.discover_creators
- 'subscribe/<str:username>/': Allows users to select a tier to subscribe to for a specific creator. View: views.select_tier
- 'subscribe/<str:username>/<int:tier_id>/': Subscribes the user to a specific tier of a creator. View: views.subscribe_to_tier
- 'subscriptions/': Displays the user's current subscriptions. View: views.subscriptions
- 'subscriptions/extend/<int:subscription_id>/': Extends the user's subscription. View: views.extend_subscription
- 'subscriptions/cancel/<int:subscription_id>/': Cancels the user's subscription. View: views.cancel_subscription
"""
