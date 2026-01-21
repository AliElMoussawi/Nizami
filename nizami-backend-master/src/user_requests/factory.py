from typing import Protocol

from src.chats.models import Chat
from src.user_requests.models import LegalAssistanceRequest
from src.users.enums import LegalCompany
from src.users.models import User


class LegalCompanyHandler(Protocol):
    def handle_request(self, user: User, chat: Chat) -> LegalAssistanceRequest:
        ...


class JPLegalHandler:
    def handle_request(self, user: User, chat: Chat) -> LegalAssistanceRequest:
        return LegalAssistanceRequest.objects.create(
            user=user,
            chat=chat,
            status='new'
        )


class LegalCompanyHandlerFactory:
    _handlers = {
        LegalCompany.JP_LEGAL.value: JPLegalHandler(),
    }
    
    @classmethod
    def get_handler(cls, company: str) -> LegalCompanyHandler:
        if not company:
            company = LegalCompany.JP_LEGAL.value
        
        handler = cls._handlers.get(company)
        if not handler:
            handler = cls._handlers[LegalCompany.JP_LEGAL.value]
        
        return handler
    
    @classmethod
    def handle_legal_assistance_request(cls, user: User, chat: Chat) -> LegalAssistanceRequest:
        company = user.get_legal_company_referrer()
        handler = cls.get_handler(company)
        return handler.handle_request(user, chat)
