from django.urls import path
from . import views

urlpatterns = [
    path('purchase/', views.purchase_points, name='purchase'),
    path('purchase-success/', views.purchase_success, name='purchase-success'),
    path('withdraw/', views.withdraw_points, name='withdraw'),
]

"""
URL patterns for the finances application.

This module defines the URL patterns for the views in the finances application, 
linking URLs to their corresponding view functions.

Patterns:
- 'purchase/': Links to the purchase_points view, allowing users to purchase points.
- 'purchase-success/': Links to the purchase_success view, handling the post-purchase process.
- 'withdraw/': Links to the withdraw_points view, allowing users to withdraw points.
"""
