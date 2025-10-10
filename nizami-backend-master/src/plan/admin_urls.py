from django.urls import path
from .views import deactivate, activate

urlpatterns = [
    path('deactivate/', deactivate, name='plan-deactivate'),
    path('activate/', activate, name='plan-activate'),
]
