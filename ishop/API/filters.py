from rest_framework import filters


class IsOwnerOrAdminFilterBackendForRefund(filters.BaseFilterBackend):
    """
    Filter that allows:
        users - to see only their own objects
        admin - all
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.all() if request.user.is_superuser else queryset.filter(purchase__customer=request.user.pk)


class IsOwnerOrAdminFilterBackendForPurchase(filters.BaseFilterBackend):
    """
    Filter that allows:
        users - to see only their own objects
        admin - all
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.all() if request.user.is_superuser else queryset.filter(customer=request.user.pk)


class IsOwnerOrAdminFilterBackendForUser(filters.BaseFilterBackend):
    """
    Filter that allows:
        users - to see only themselves
        admin - all
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.all() if request.user.is_superuser else queryset.filter(pk=request.user.pk)
