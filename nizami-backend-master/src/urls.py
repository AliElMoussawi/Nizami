"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from src import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/auth/', include('src.authentication.urls')),
    path('api/v1/admin/users/', include('src.users.urls')),
    path('api/v1/admin/reference-documents/', include('src.reference_documents.urls')),
    path('api/v1/admin/dashboard/', include('src.dashboard.urls')),
    path('api/v1/admin/prompts/', include('src.prompts.urls')),
    path('api/v1/chats/', include('src.chats.urls')),
    #Plan
    path('api/v1/admin/plans/', include('src.plan.admin_urls')),
    path('api/v1/plans/', include('src.plan.urls')),
    #Payment
    path('api/v1/payment/', include('src.payment.urls')),
    path('api/v1/admin/payments/', include('src.payment.admin_urls')),
    #Subscription
    path('api/v1/subscriptions/', include('src.subscription.urls')),
    path('api/v1/admin/subscriptions/', include('src.subscription.admin_urls')),
    #User Requests
    path('api/v1/user-requests/', include('src.user_requests.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
