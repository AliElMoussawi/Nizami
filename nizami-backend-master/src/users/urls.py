from django.urls import path

from .views import ListUserViewSet, CreateDeleteUserViewSet, UpdateUserViewSet, \
    UpdateUserPasswordViewSet, UpdateUserStatusViewSet

urlpatterns = [
    path('<int:pk>/edit', UpdateUserViewSet.as_view({'put': 'update'})),
    path('<int:pk>/update-status', UpdateUserStatusViewSet.as_view({'put': 'update'})),
    path('<int:pk>/update-password', UpdateUserPasswordViewSet.as_view({'put': 'update'})),

    path('<int:pk>', CreateDeleteUserViewSet.as_view({'delete': 'destroy'})),
    path('<int:pk>/get', ListUserViewSet.as_view({'get': 'retrieve'})),

    path('get', ListUserViewSet.as_view({'post': 'list'})),
    path('', CreateDeleteUserViewSet.as_view({'post': 'create'})),
]
