from django.urls import path
from .views import get, get_by_uuid, available_for_upgrade

urlpatterns = [
    path('', get, name='plan-list'),
    path('<uuid:uuid>', get_by_uuid, name='plan-detail'),
    path('available-for-upgrade', available_for_upgrade, name='can_upgrade_to_plans')
]



