from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.payment.models import MoyasarPayment
from src.payment.serializers.moyasar_serializers import PaymentDetailSerializer
from src.common.mixins import ForceDatatablesFormatMixin
from src.common.permissions import IsAdminPermission


class ListPaymentViewSet(ForceDatatablesFormatMixin, ReadOnlyModelViewSet):
    queryset = MoyasarPayment.objects.select_related('source', 'invoice').all().order_by('-created_at')
    serializer_class = PaymentDetailSerializer
    pagination_class = DatatablesPageNumberPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]
    lookup_field = 'internal_uuid'

    def filter_queryset(self, queryset):
        status_filter = self.request.data.get('status', None)
        search_term = self.request.data.get('search_term', None)
        date_from = self.request.data.get('date_from', None)
        date_to = self.request.data.get('date_to', None)
        date_filter = self.request.data.get('date_filter', None)
        currency = self.request.data.get('currency', None)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if search_term:
            queryset = queryset.filter(
                Q(description__icontains=search_term) |
                Q(id__icontains=search_term) |
                Q(metadata__user_id__icontains=search_term)
            )

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass

        if date_filter:
            try:
                date_filter_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date=date_filter_obj)
            except ValueError:
                pass

        if currency:
            queryset = queryset.filter(currency=currency)

        return queryset


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def payment_statistics(request: Request):
    """
    Get basic payment counts for admin dashboard
    """
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    # Basic count only
    total_payments = MoyasarPayment.objects.filter(
        created_at__range=[start_date, end_date]
    ).count()

    return Response({
        'summary': {
            'total_payments': total_payments,
            'period_days': days
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def total_payments_count(request: Request):
    """
    Get total payments count (all time)
    """
    total_count = MoyasarPayment.objects.count()
    
    return Response({
        'total_count': total_count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def payment_details(request: Request, payment_id):
    """
    Get detailed payment information for admin
    """
    try:
        payment = MoyasarPayment.objects.select_related(
            'source', 'invoice', 'subscription_link__user_subscription__user'
        ).get(internal_uuid=payment_id)
        
        serializer = PaymentDetailSerializer(payment)
        
        # Add additional admin-specific information
        data = serializer.data
        data['admin_info'] = {
            'ip_address': payment.ip,
            'user_agent': payment.metadata.get('user_agent'),
            'subscription_link': None
        }
        
        # Check if payment is linked to a subscription
        try:
            subscription_link = payment.subscription_link
            if subscription_link:
                data['admin_info']['subscription_link'] = {
                    'subscription_uuid': str(subscription_link.user_subscription.uuid),
                    'user_email': subscription_link.user_subscription.user.email,
                    'plan_name': subscription_link.user_subscription.plan.name
                }
        except AttributeError:
            # Payment is not linked to a subscription
            pass
        
        return Response(data, status=status.HTTP_200_OK)
        
    except MoyasarPayment.DoesNotExist:
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
