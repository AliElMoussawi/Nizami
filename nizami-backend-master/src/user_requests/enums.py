from enum import Enum


class LegalAssistanceRequestStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
