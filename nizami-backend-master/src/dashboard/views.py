from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..chats.models import Chat, Message
from ..common.permissions import IsAdminPermission
from ..reference_documents.models import ReferenceDocument, RagSourceDocument
from ..settings import RAG_SOURCE
from ..users.models import User


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def get_cards(request):
    return Response([
        {
            'icon': 'heroUsers',
            'title': 'Users',
            'body': User.objects.count(),
        },
        {
            'icon': 'heroChatBubbleOvalLeftEllipsis',
            'title': 'Chats',
            'body': Chat.objects.count(),
        },
        {
            'icon': 'heroDocument',
            'title': 'Documents (Reference)' if RAG_SOURCE == 'new' else 'Documents',
            'body': ReferenceDocument.objects.count(),
        },
        *(
            [{
                'icon': 'heroDocument',
                'title': 'Documents (RAG Source)',
                'body': RagSourceDocument.objects.filter(is_embedded=True).count(),
            }] if RAG_SOURCE == 'new' else []
        ),
        {
            'icon': 'heroChatBubbleBottomCenterText',
            'title': 'Messages',
            'body': Message.objects.count(),
        },
    ])
