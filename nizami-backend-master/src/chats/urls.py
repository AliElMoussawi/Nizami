from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from src.chats.flow import build_graph
from src.chats.views import CreateChatViewSet, ListChatsViewSet, ListMessagesViewSet, CreateMessageViewSet, \
    RetrieveChatViewSet, CreateMessageFileViewSet, DownloadFileViewSet, DeleteChatViewSet, UpdateChatViewSet


@api_view(['GET'])
def test(request):
    graph = build_graph()

    print(graph.get_graph().draw_mermaid())

    return Response(graph.invoke({'input': request.query_params['text']}))


urlpatterns = [
    path('test', test),
    path('<int:pk>/delete', DeleteChatViewSet.as_view({'delete': 'destroy'})),
    path('<int:pk>/update', UpdateChatViewSet.as_view({'put': 'update'})),
    path('<int:pk>', RetrieveChatViewSet.as_view({'get': 'retrieve'})),
    path('', CreateChatViewSet.as_view({'post': 'create'})),

    path('get', ListChatsViewSet.as_view({'get': 'list'})),

    path('<int:chat_id>/messages', ListMessagesViewSet.as_view({'get': 'list'})),
    path('messages/create', CreateMessageViewSet.as_view({'post': 'create'})),

    path('messages/upload-file', CreateMessageFileViewSet.as_view({'post': 'create'})),

    path('file-messages/<int:pk>/get-file', DownloadFileViewSet.as_view({'get': 'retrieve'})),
]
