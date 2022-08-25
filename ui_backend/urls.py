from django.urls import path, re_path

from .controllers import Root, Controller, Authorizations, History, UiConfiguration


urlpatterns = [
    path('backend/', Root.RootController.as_view()),

    path('backend/authorizations/', Authorizations.AuthorizationsController.as_view()),
    path('backend/history/', History.HistoryController.as_view()),
    path('backend/ui-config/', UiConfiguration.UiConfigurationController.as_view()),

    re_path(r'^backend/.*/.*', Controller.Controller.as_view()),
]
