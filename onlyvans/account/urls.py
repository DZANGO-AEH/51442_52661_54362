from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name="register"),
    path('login', views.userlogin, name="login"),
    path('logout', views.userlogout, name="logout"),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('profile/create-stripe-account/', views.create_stripe_account, name='create_stripe_account'),
    path('profile/change-password/', views.change_password, name='change-password'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('history/', views.event_history, name='history'),
]