import os
import importlib
from django.urls import path, re_path

from .controllers import Root, Controller, History, UiConfiguration, Authorizations
from .controllers.Workflow import Workflows, FlowTest1
from .controllers.Permission import WorkflowPermissions, WorkflowPermission, ApiIdentityGroups
from .controllers import RawTxtController, About

urlpatterns = [
    path('backend/', Root.RootController.as_view()),

    path('backend/authorizations/', Authorizations.AuthorizationsController.as_view()),
    path('backend/history/', History.HistoryController.as_view()),
    path('backend/ui-config/', UiConfiguration.UiConfigurationController.as_view()),
    path('backend/about/', About.AboutController.as_view()),

    path('backend/identity-groups/', ApiIdentityGroups.ApiIdentityGroupsController.as_view()),

    path('backend/workflow-permissions/', WorkflowPermissions.WorkflowPermissionsController.as_view()),
    path('backend/workflow-permission/<str:workflow>/<str:identityGroup>/', WorkflowPermission.WorkflowPermissionController.as_view()),

    path('backend/workflows/', Workflows.WorkflowsController.as_view()),
    path('backend/ui-backend/doc/<str:fileName>/', RawTxtController.RawTxtController.as_view(), name='txt'),

    path('backend/workflow/flow-test1/', FlowTest1.WorkflowFlowTest1Controller.as_view()),
]

# Add usecases urls.
try:
    modules = os.listdir(os.path.dirname("/var/www/ui-backend/ui_backend/urlsUsecases/"))
except Exception:
    modules = []

for fileModule in modules:
    try:
        if fileModule == '__init__.py' or fileModule[-3:] != '.py':
            continue
        module = importlib.import_module("ui_backend.urlsUsecases." + fileModule[:-3], package=None)

        # Replace.
        try:
            replaceUrlpatterns = getattr(module, 'replaceUrlpatterns')
            if replaceUrlpatterns:
                for path in reversed(urlpatterns):
                    for replacePath in replaceUrlpatterns:
                        if path.pattern._route == replacePath.pattern._route: # call another controller.
                            urlpatterns.remove(path)
                            urlpatterns.append(replacePath)

        except Exception:
            pass

        # Add.
        usecaseUrlpatterns = getattr(module, 'urlpatterns')
        urlpatterns.extend(usecaseUrlpatterns)

    except Exception:
        pass

urlpatterns.append(re_path(r'^backend/.*/.*', Controller.Controller.as_view()))
from. helpers.Log import Log
Log.log(urlpatterns, 'UUUUUUUUUUUUUUUUUUUUUU')