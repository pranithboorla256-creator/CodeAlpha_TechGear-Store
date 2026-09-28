from django.contrib import admin
from .models import Order, OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "quantity")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "total", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status", "payment_method", "created_at")
    search_fields = ("number", "user__username", "email", "full_name")
    list_editable = ("status", "payment_status")
    inlines = (OrderItemInline,)
