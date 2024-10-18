from django.urls import path, re_path

from .controllers import Root, Controller, History, UiConfiguration, Authorizations
from .controllers.Workflow import Workflows, FlowTest1, CheckPointAddHost, CheckPointRemoveHost, CloudAccount, CloudAccounts
from .controllers.Permission import WorkflowPermissions

urlpatterns = [
    path('backend/', Root.RootController.as_view()),

    path('backend/authorizations/', Authorizations.AuthorizationsController.as_view()),
    path('backend/history/', History.HistoryController.as_view()),
    path('backend/ui-config/', UiConfiguration.UiConfigurationController.as_view()),

     path('backend/workflow-permissions/', WorkflowPermissions.WorkflowPermissionsController.as_view()),


    path('backend/workflows/', Workflows.WorkflowsController.as_view()),
    path('backend/workflow/flow-test1/', FlowTest1.WorkflowFlowTest1Controller.as_view()),
    path('backend/workflow/checkpoint-add-host/', CheckPointAddHost.WorkflowFlowCheckPointAddHostController.as_view()),
    path('backend/workflow/checkpoint-remove-host/', CheckPointRemoveHost.WorkflowCheckPointRemoveHostController.as_view()),
    path('backend/workflow/cloud-account/<str:accountName>/', CloudAccount.WorkflowCloudAccountController.as_view()),
    path('backend/workflow/cloud-accounts/', CloudAccounts.WorkflowCloudAccountsController.as_view()),

    re_path(r'^backend/.*/.*', Controller.Controller.as_view()),
]
