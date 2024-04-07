from django.urls import path
from . import views


app_name = 'client'

urlpatterns = [
    path('dashboard', views.dashboard, name="dashboard"),

]