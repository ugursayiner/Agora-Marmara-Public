from django.urls import path
from . import views

urlpatterns = [
    path('signin/' , views.open_signin , name='authentications_signin_name'),
    path('signup/' , views.open_signup , name='authentications_signup_name'),
    path("logout/", views.user_logout , name="authentications_logout_name")
]

