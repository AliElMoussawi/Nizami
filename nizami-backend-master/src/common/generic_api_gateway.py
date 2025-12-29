import json
import logging
from typing import Dict, Any, Type

from django.db import models
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from rest_framework import serializers

logger = logging.getLogger()


class APIGatewayException(Exception):
    def __init__(self, status, msg, source):
        self.status = status
        self.msg = msg
        self.source = source

    def get_message(self):
        return self.msg

    def get_status(self):
        return self.status
    def get_source(self):
        return self.source

class APIGateway(object):
    API_URL = None
    SOURCE = ''
    # retry feature defaults
    DEFAULT_RETRY = 5
    DEFAULT_BACKOFF_FACTOR = 2
    DEFAULT_STATUS_FORCELIST = (429,) 


    @classmethod
    def build_url(cls, uri) -> str:
        return uri
    
    def get_auth_header(cls) -> dict:
        return {}

    def get_auth(cls) -> dict:
        return ()

    def get_default_headers(self):
        headers = dict(self.get_auth_header())
        return headers

    def get_request_kwargs(self, with_ssl_verification=True):
        return {
            'auth': self.get_auth(),
            'verify': with_ssl_verification
        }

    @classmethod
    def req_with_retry(cls, retries=DEFAULT_RETRY, backoff_factor=DEFAULT_BACKOFF_FACTOR, status_forcelist=DEFAULT_STATUS_FORCELIST, session=None,):
        """
        this returns a session that functions like the requests module but with retries built it for certain status codes
        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def send_request(self, url:str, method: str, data:dict = None, headers:dict=None, parse_data=True, with_ssl_verification=True):
        if not data:
            data = {}
        json_data = json.dumps(data, default=str) if parse_data else data
        if not headers:
            headers = dict(**self.get_default_headers())

        requests_kwargs = dict(headers=headers, **self.get_request_kwargs(with_ssl_verification=with_ssl_verification))
        request_session = self.req_with_retry()
        if method == "GET":
            resp = request_session.get(url, timeout=10, **requests_kwargs)
        elif method == "POST":
           resp = request_session.post(url, data=json_data, timeout=10, **requests_kwargs)
        elif method == "PATCH":
           resp = request_session.patch(url, data=json_data, timeout=10, **requests_kwargs)
        elif method == "PUT":
           resp = request_session.put(url, data=json_data, timeout=10, **requests_kwargs)
        elif method == "DELETE":
           resp = request_session.delete(url, data=json_data, timeout=10, **requests_kwargs)
        try:
            assert resp.ok
        except Exception:
            exception_dict = dict(url=url, method=method, data=self.recursive_obfuscate(json.loads(json_data)), status_code=resp.status_code, resp_text=resp.text)
            logger.exception(exception_dict)
            raise APIGatewayException(resp.status_code, resp.text, self.SOURCE)

        return json.loads(resp.text)

    def recursive_obfuscate(self, body):
        keys_to_obfuscate = ['password', 'new_password', 'old_password', 'confirm_password']
        for key in body:
            if key in keys_to_obfuscate:
                body[key] = '****'  # replace the matched value
            elif isinstance(body[key], dict):
                self.recursive_obfuscate(body[key])

        return body


def validate_and_log_response(
    response_data: Dict[str, Any],
    serializer_class: Type[serializers.Serializer],
    operation: str,
    source: str = "External API"
) -> Dict[str, Any]:
    """
    This function ensures data integrity when receiving responses from external APIs.
    It validates the structure, logs unexpected changes, and prevents invalid data
    from reaching the application layer.
    """
    serializer = serializer_class(data=response_data)
    
    try:
        if not serializer.is_valid():
            logger.error(
                f"{source} API response validation failed for {operation}. "
                f"Errors: {serializer.errors}. "
                f"Response: {response_data}"
            )
            raise serializers.ValidationError(
                f"Invalid {source} {operation} response: {serializer.errors}"
            )
        
        logger.info(f"{source} {operation} response validated successfully")
        return serializer.validated_data
        
    except serializers.ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(
            f"Exception during {source} response validation for {operation}: {str(e)}. "
            f"Response: {response_data}"
        )
        raise

class WebhookProcessingStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    VALIDATION_ERROR = "validation_error", "Validation error"
    PROCESSING_ERROR = "processing_error", "Processing error"
    DUPLICATE_EVENT = "duplicate_event", "Duplicate event"
    INVALID_EVENT_TYPE = "invalid_event_type", "Invalid event type"
