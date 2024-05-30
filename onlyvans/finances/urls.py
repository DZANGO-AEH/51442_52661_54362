from django.urls import path
from . import views

urlpatterns = [
    path('purchase/', views.purchase_points, name='purchase'),
    path('purchase-success/', views.purchase_success, name='purchase-success'),
    path('withdraw/', views.withdraw_points, name='withdraw'),
    ]