from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'id', 'razor_pay_order_id', 'razor_pay_payment_id', 'razor_pay_payment_signature', 'status', 'created_at']
    search_fields = ['razor_pay_order_id']