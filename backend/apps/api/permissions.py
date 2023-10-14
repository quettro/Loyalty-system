from rest_framework.permissions import BasePermission


class IsPartner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_partner


class IsAcceptedContract(BasePermission):
    def has_permission(self, request, view):
        return request.user.get_partner().is_contract


class IsAccessToTheSection(BasePermission):
    def __init__(self, codename):
        self.codename = codename

    def has_permission(self, request, view):
        permissions = request.user.get_permissions()
        permissions = permissions.filter(codename=self.codename)

        if not request.user.is_partner:
            permissions = permissions.filter(is_partners=False)

        return permissions.exists()
