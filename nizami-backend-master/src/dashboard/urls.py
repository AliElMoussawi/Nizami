from django.urls import path

from src.dashboard.views import get_cards

urlpatterns = [
    path('cards', get_cards),
]
