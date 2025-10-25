from django.urls import path
from .admin_views import (
    ListPaymentViewSet,
    payment_statistics,
    payment_details,
    total_payments_count
)

urlpatterns = [
    path('get', ListPaymentViewSet.as_view({'post': 'list'}), name='admin-payment-list'),
    path('statistics', payment_statistics, name='admin-payment-statistics'),
    path('total-count', total_payments_count, name='admin-payment-total-count'),
    path('<uuid:payment_id>/details', payment_details, name='admin-payment-details'),
]
