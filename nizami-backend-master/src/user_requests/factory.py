from typing import Protocol

from src.chats.models import Chat
from src.user_requests.models import LegalAssistanceRequest
from src.users.enums import LegalCompany
from src.users.models import User


class LegalCompanyHandler(Protocol):
    """Protocol for legal company handlers"""
    
    def handle_request(self, user: User, chat: Chat) -> LegalAssistanceRequest:
        """Handle the legal assistance request for this legal company"""
        ...


class JPLegalHandler:
    """Handler for JP Legal company"""
    
    def handle_request(self, user: User, chat: Chat) -> LegalAssistanceRequest:
        """Create a legal assistance request record for JP Legal"""
        return LegalAssistanceRequest.objects.create(
            user=user,
            chat=chat,
            status='new'
        )


class LegalCompanyHandlerFactory:
    """Factory for creating legal company handlers"""
    
    _handlers = {
        LegalCompany.JP_LEGAL.value: JPLegalHandler(),
    }
    
    @classmethod
    def get_handler(cls, company: str) -> LegalCompanyHandler:
        """
        Get the appropriate handler for the given legal company.
        Defaults to JP_LEGAL if company is None or not found.
        """
        if not company:
            company = LegalCompany.JP_LEGAL.value
        
        handler = cls._handlers.get(company)
        if not handler:
            # Default to JP_LEGAL if company not found
            handler = cls._handlers[LegalCompany.JP_LEGAL.value]
        
        return handler
    
    @classmethod
    def handle_legal_assistance_request(cls, user: User, chat: Chat) -> LegalAssistanceRequest:
        """
        Handle a legal assistance request using the appropriate handler based on user's legal company referrer.
        """
        company = user.get_legal_company_referrer()
        handler = cls.get_handler(company)
        return handler.handle_request(user, chat)
