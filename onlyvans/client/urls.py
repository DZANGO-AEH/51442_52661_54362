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