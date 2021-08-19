from rest_framework.permissions import BasePermission


class GranularIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        # Client CORS preflight calls must be unauthenticated!
        # This was useful only if the REACT UI insists directly on this ui-backend via XHR (CORS) and authentication is enabled.
        # Historical but kept for possible future use.
        unsafeMethods = ['OPTIONS']

        if request.method in unsafeMethods:
            return True
        else:
            return bool(request.user and request.user.is_authenticated)
