from django.urls import path


from src.subscription.views import history, current_subscription, latest, deactivate


urlpatterns = [
    path('history/', history, name='subscription-history'),
    path('current/', current_subscription, name='subscription-active'),
    path('latest/', latest, name='subscription-latest'),
    path('deactivate/', deactivate, name='subscription-deactivation')

]


