from django.urls import path
from . import views


app_name = 'creator'
urlpatterns = [
    path('dashboard', views.dashboard, name="dashboard"),

]