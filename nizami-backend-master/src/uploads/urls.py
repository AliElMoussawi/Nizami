from django.urls import path

from src.uploads.views import CompleteUploadView, InitUploadView, UploadProxyView

urlpatterns = [
    path("init", InitUploadView.as_view()),
    path("upload-proxy", UploadProxyView.as_view(), name="uploads-upload-proxy"),
    path("complete", CompleteUploadView.as_view()),
]
