from django.urls import path

from .views import register, login, forgot_password, reset_password, get_profile, update_profile, update_password

urlpatterns = [
    path('register', register),
    path('login', login),
    path('forgot-password', forgot_password),
    path('reset-password', reset_password),
    path('profile', get_profile),
    path('update-profile', update_profile),
    path('update-password', update_password),
]
