from django.urls import path, re_path

from .controllers import Root, Controller, Authorizations, History, UiConfiguration
from .controllers.Permission import Roles, IdentityGroup, IdentityGroups, Permission, Permissions, Workflows, Authorizations as OwnAuthorizations
from .controllers.Workflow.checkpoint import Host as CheckPointHost, Hosts as CheckPointHosts

urlpatterns = [
    path('backend/', Root.RootController.as_view()),

    path('backend/authorizations/', Authorizations.AuthorizationsController.as_view()),
    path('backend/history/', History.HistoryController.as_view()),
    path('backend/ui-config/', UiConfiguration.UiConfigurationController.as_view()),

    path('backend/workflow/authorizations/', OwnAuthorizations.AuthorizationsController.as_view()),
    path('backend/workflow/workflows/', Workflows.WorkflowsController.as_view()),
    path('backend/workflow/roles/', Roles.PermissionRolesController.as_view()),
    path('backend/workflow/identity-groups/', IdentityGroups.PermissionIdentityGroupsController.as_view()),
    path('backend/workflow/identity-group/<str:identityGroupIdentifier>/', IdentityGroup.PermissionIdentityGroupController.as_view()),

    path('backend/workflow/permissions/', Permissions.PermissionsController.as_view()),
    path('backend/workflow/permission/<int:permissionId>/', Permission.PermissionController.as_view()),

    # Workflows.
    path('backend/workflow/checkpoint/add-host/', CheckPointHosts.CheckPointHostsController.as_view()),
    path('backend/workflow/checkpoint/remove-host/', CheckPointHost.CheckPointRemoveHostController.as_view()),

    re_path(r'^backend/.*/.*', Controller.Controller.as_view()),
]
