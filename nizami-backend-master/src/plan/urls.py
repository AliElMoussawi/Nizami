from django.urls import path
from .views import deactivate, activate, get, get_by_uuid

urlpatterns = [
    path('', get, name='plan-list'),
    path('<uuid:uuid>', get_by_uuid, name='plan-detail'),
]



