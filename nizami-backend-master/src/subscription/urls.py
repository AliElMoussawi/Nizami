from django.urls import path

from src.subscription.views import history, active


urlpatterns = [
    path('history', history, name='subscription-history'),
    path('active', active, name='subscription-active'),
]


