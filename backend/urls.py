from django.urls import include, path

urlpatterns = [
    path('', include('ui_backend.urls')),
]
