from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name=""),
    path('register', views.register, name="register"),
    path('login', views.userlogin, name="login"),
    path('logout', views.userlogout, name="logout"),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('profile/change-password/', views.change_password, name='change-password'),
    path('profile/<str:username>/', views.profile, name='profile'),

]