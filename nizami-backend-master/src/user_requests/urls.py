from django.urls import path

from src.user_requests.views import (
    CreateLegalAssistanceRequestViewSet,
    ListLegalAssistanceRequestsViewSet,
    UpdateLegalAssistanceRequestStatusViewSet,
)

urlpatterns = [
    path('', CreateLegalAssistanceRequestViewSet.as_view({'post': 'create'})),
    path('admin/', ListLegalAssistanceRequestsViewSet.as_view({'get': 'list'})),
    path('admin/<int:pk>/', UpdateLegalAssistanceRequestStatusViewSet.as_view({'patch': 'partial_update', 'put': 'update'})),
]
