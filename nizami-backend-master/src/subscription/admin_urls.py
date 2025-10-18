from django.urls import path

from .admin_views import (
    ListUserSubscriptionViewSet, 
    CreateUserSubscriptionViewSet, 
    UpdateUserSubscriptionViewSet,
    activate_subscription,
    deactivate_subscription
)

urlpatterns = [
    path('<uuid:uuid>/edit', UpdateUserSubscriptionViewSet.as_view({'put': 'update'})),
    path('<uuid:uuid>/activate', activate_subscription),
    path('<uuid:uuid>/deactivate', deactivate_subscription),
    path('<uuid:uuid>/get', ListUserSubscriptionViewSet.as_view({'get': 'retrieve'})),
    path('get', ListUserSubscriptionViewSet.as_view({'post': 'list'})),
    path('', CreateUserSubscriptionViewSet.as_view({'post': 'create'})),
]
