from django.urls import path
from .views import deactivate, activate, admin_list, admin_create, admin_update

urlpatterns = [
    path('deactivate/', deactivate, name='plan-deactivate'),
    path('activate/', activate, name='plan-activate'),
    path('', admin_list, name='admin-plan-list'),
    path('create/', admin_create, name='admin-plan-create'),
    path('<uuid:uuid>/', admin_update, name='admin-plan-update'),
]
