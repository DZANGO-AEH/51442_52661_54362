from django.urls import path
from . import views

app_name = 'creator'
urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('create-post/', views.create_post, name="create-post"),
    path('tiers/', views.tiers, name="tiers"),
    path('tiers/create/', views.create_tier, name="create-tier"),
    path('tiers/delete/<int:tier_id>/', views.delete_tier, name='delete-tier'),
]
