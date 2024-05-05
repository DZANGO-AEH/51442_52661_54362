from django.urls import path
from . import views


app_name = 'client'

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('subscribe/<str:username>/', views.select_tier, name='select-tier'),
    path('subscribe/<str:username>/<int:tier_id>/', views.subscribe_to_tier, name='subscribe-to-tier'),
    path('stripe-success/', views.stripe_success, name='stripe-success'),
    path('stripe-cancel/', views.stripe_cancel, name='stripe-cancel'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
]