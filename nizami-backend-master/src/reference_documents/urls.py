from django.urls import path

from .views import ListReferenceDocumentViewSet, CreateReferenceDocumentViewSet, RetrieveReferenceDocumentViewSet, \
    DeleteReferenceDocumentViewSet, UpdateReferenceDocumentViewSet

urlpatterns = [
    path('<int:pk>/edit', UpdateReferenceDocumentViewSet.as_view({'put': 'update'})),

    path('get', ListReferenceDocumentViewSet.as_view({'post': 'list'})),
    path('', CreateReferenceDocumentViewSet.as_view({'post': 'create'})),

    path('<int:pk>/get', ListReferenceDocumentViewSet.as_view({'get': 'retrieve'})),
    path('<int:pk>/get-file', RetrieveReferenceDocumentViewSet.as_view({'get': 'retrieve'})),

    path('<int:pk>', DeleteReferenceDocumentViewSet.as_view({'delete': 'destroy'})),
]
