from django.urls import path

from src.subscription.views import history, active, deactivate


urlpatterns = [
    path('history', history, name='subscription-history'),
    path('active', active, name='subscription-active'),
    path('deactivate', deactivate, name='subscription-deactivation')
]


