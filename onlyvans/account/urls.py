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

"""
URL configuration for the account application.

Each path function specifies a URL pattern and the view that should handle
requests to that pattern. Additionally, a name is provided for each URL pattern
to make it easier to refer to them in templates and other parts of the application.

Paths:
- '' (home): Handles the home page. View: views.home
- 'register': Handles user registration. View: views.register
- 'login': Handles user login. View: views.userlogin
- 'logout': Handles user logout. View: views.userlogout
- 'profile/update/': Handles profile updates. View: views.update_profile
- 'profile/create-stripe-account/': Handles creating Stripe accounts for users. View: views.create_stripe_account
- 'profile/change-password/': Handles changing user passwords. View: views.change_password
- 'profile/<str:username>/': Displays user profiles. View: views.profile
- 'history/': Displays user event history. View: views.event_history
"""
