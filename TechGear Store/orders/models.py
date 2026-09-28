import uuid
from django.conf import settings
from django.db import models
from products.models import Product

class Order(models.Model):
    STATUS = [(v,v.replace("_", " ").title()) for v in ("pending", "processing", "shipped", "delivered", "cancelled")]
    PAYMENT = [("cod", "Cash on Delivery"), ("upi", "UPI"), ("card", "Credit / Debit Card")]
    PAYMENT_STATUS = [("pending","Pending"),("paid","Paid"),("failed","Failed")]
    number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=12)
    payment_method = models.CharField(max_length=10, choices=PAYMENT)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="pending")
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"Order {self.number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    @property
    def line_total(self): return self.unit_price * self.quantity
