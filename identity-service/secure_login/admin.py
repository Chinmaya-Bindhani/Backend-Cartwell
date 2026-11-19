from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import SellerApplicationModel as SellerApplication, CustomUser

@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "business_name",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    ]

    list_filter = ["status", "created_at"]
    search_fields = [
        "user__email",
        "user__phone_number",
        "business_name",
        "aadhaar_number",
        "pan_number",
        "gstin_number",
    ]

    readonly_fields = [
        "user",
        "business_name",
        "business_address",
        "aadhaar_number",
        "pan_number",
        "gstin_number",
        "reviewed_by",
        "reviewed_at",
        "created_at",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if obj.status == SellerApplication.Status.REJECTED:
            if not obj.rejection_reason.strip():
                raise ValidationError(
                    "A rejection reason is required when rejecting an application."
                )

        if obj.status in {
            SellerApplication.Status.APPROVED,
            SellerApplication.Status.REJECTED,
        }:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

        if obj.status == SellerApplication.Status.APPROVED:
            user = obj.user
            user.role = CustomUser.Role.SELLER
            user.save(update_fields=["role"])