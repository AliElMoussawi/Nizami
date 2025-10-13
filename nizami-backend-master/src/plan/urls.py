from django.urls import path
from .views import get, get_by_uuid, available_for_upgrade, get_current_user_plan_default_configuration, activate, deactivate

urlpatterns = [
    path('', get, name='plan-list'),
    path('<uuid:uuid>', get_by_uuid, name='plan-detail'),
    path('available-for-upgrade', available_for_upgrade, name='can_upgrade_to_plans'),
    path('subscribed-configuration', get_current_user_plan_default_configuration, name='subscribed_plan_default_activation'),
    path('activate', activate, name='activate-plan-admin'),
    path('deactivate', deactivate, name='deactivate-plan-admin'),
    

]



