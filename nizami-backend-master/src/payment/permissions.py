from src import settings
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
import logging
import hmac

logger = logging.getLogger(__name__)

class IsValidMoyasarSignature(BasePermission):
    def _verify_is_moyasar_secret_token(self, secret_token):
        return hmac.compare_digest(secret_token, settings.MOYASAR_WEBHOOK_SECRET_KEY)
    def has_permission(self, request, view):
        secret_token = request.data.get("secret_token", '')
        if not secret_token:
            logger.warning("Missing Moyasar webhook signature.")
            raise PermissionDenied("Missing Moyasar webhook signature fields.")
        
        valid_moyasar_signature = self._verify_is_moyasar_secret_token(secret_token=secret_token)
        if not valid_moyasar_signature:
            logger.warning("Invalid Moyasar webhook signature.")
            raise PermissionDenied("Invalid Moyasar signature.")

        return True
    