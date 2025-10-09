from django.urls import path

from src.prompts.views import UpdatePromptViewSet, ListPromptViewSet

urlpatterns = [
    path('<int:pk>/edit', UpdatePromptViewSet.as_view({'put': 'update'})),

    path('get', ListPromptViewSet.as_view({'post': 'list'})),
]
