from django.urls import path

from apps.users_upload.views import FileUploadView,QueryBuilderView,IndustryDropdownView,LocalityDropdownView

urlpatterns = [
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/query-builder/', QueryBuilderView.as_view(), name='query-builder'),
    path('api/industry-dropdown/', IndustryDropdownView.as_view(), name='industry-dropdown'),
    path('api/locality-dropdown/', LocalityDropdownView.as_view(), name='locality-dropdown'),
]
