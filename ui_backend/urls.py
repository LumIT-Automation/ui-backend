from django.urls import path, re_path, include

from .controllers import Root, Controller, Authorizations


urlpatterns = [
    path('backend/', Root.RootController.as_view()),

    path('backend/authorizations/', Authorizations.AuthorizationsController.as_view()),

    re_path(r'^backend/.*/.*', Controller.Controller.as_view()),
]
