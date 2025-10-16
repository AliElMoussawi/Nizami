from django.urls import path
from .views import (
    MoyasarWebhookView,
    list_payments,
    PaymentDetailView,
    SyncPaymentStatusView,
    UserPaymentSourceListView,
    PaymentSourceDetailView,
)

urlpatterns = [
    path('', list_payments, name='payment-list'),
    path('<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('<uuid:payment_id>/sync/', SyncPaymentStatusView.as_view(), name='sync-payment'),
    
    path('webhooks/moyasar/', MoyasarWebhookView.as_view(), name='moyasar-webhook'),
    
    path('sources/', UserPaymentSourceListView.as_view(), name='list-payment-sources'),
    path('sources/<uuid:source_id>/', PaymentSourceDetailView.as_view(), name='payment-source-detail'),
]

