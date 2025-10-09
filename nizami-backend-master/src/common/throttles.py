from rest_framework.throttling import UserRateThrottle


class ForgotPasswordThrottle(UserRateThrottle):
    rate = '1/min'  # Enforce a single request per minute for this endpoint
