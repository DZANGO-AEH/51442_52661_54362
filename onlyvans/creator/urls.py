from django.urls import path
from . import views

app_name = 'creator'

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('create-post/', views.create_post, name="create-post"),
    path('tiers/', views.tiers, name="tiers"),
    path('tiers/create/', views.create_tier, name="create-tier"),
    path('tiers/delete/<int:tier_id>/', views.delete_tier, name='delete-tier'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
]

"""
URL configuration for the creator application.

Paths:
- 'dashboard/': Handles the creator's dashboard. View: views.dashboard
- 'create-post/': Handles the creation of a new post. View: views.create_post
- 'tiers/': Displays all tiers created by the creator. View: views.tiers
- 'tiers/create/': Handles the creation of a new tier. View: views.create_tier
- 'tiers/delete/<int:tier_id>/': Handles the deletion of a tier specified by tier_id. View: views.delete_tier
- 'post/<int:post_id>/delete/': Handles the deletion of a post specified by post_id. View: views.post_delete
"""
