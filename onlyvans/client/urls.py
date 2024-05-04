from django.urls import path
from . import views


app_name = 'client'

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('subscribe/<str:username>/', views.select_tier, name='select-tier'),
    path('subscribe/<str:username>/<int:tier_id>/', views.subscribe_to_tier, name='subscribe-to-tier'),
    path('unsubscribe/<str:username>/<int:tier_id>/', views.cancel_paypal_subscription, name='cancel-paypal-subscription'),
    path('subscribe/<str:username>/<int:tier_id>/execute/', views.execute_paypal_subscription, name='execute-paypal-subscription'),
]