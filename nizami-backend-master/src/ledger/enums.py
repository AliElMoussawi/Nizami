from enum import Enum


class SubscriptionValidationCode(str, Enum):
    USER_INACTIVE = "user_inactive"
    SUBSCRIPTION_NOT_FOUND = "subscription_not_found"
    SUBSCRIPTION_MULTIPLE_ACTIVE = "subscription_multiple_active"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    SUBSCRIPTION_INACTIVE = "subscription_inactive"
    NO_MESSAGE_CREDITS = "no_message_credits"
    GENERAL_ERROR = "an_error_has_occured"


