from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "type",
        "borrowing_id",
        "session_id",
        "money_to_pay",
    )
    list_filter = ("status", "type")
    search_fields = ("session_id",)
