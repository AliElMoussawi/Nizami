import logging
from .payment_service import PaymentService
from ..adapters.moyasar.gateway import MoyasarGateway

logger = logging.getLogger(__name__)


def get_moyasar_payment_service() -> PaymentService:
    return PaymentService(gateway=MoyasarGateway())
