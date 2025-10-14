from django.urls import path

from src.subscription.views import history, active, latest, deactivate


urlpatterns = [
    path('history/', history, name='subscription-history'),
    path('active/', active, name='subscription-active'),
    path('latest/', latest, name='subscription-latest'),
    path('deactivate/', deactivate, name='subscription-deactivation')
]


