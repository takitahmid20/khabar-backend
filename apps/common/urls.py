from django.urls import path

from apps.common.views.upload_viewset import UploadViewSet

urlpatterns = [
    path("upload", UploadViewSet.as_view({"post": "create"}), name="file-upload"),
]
