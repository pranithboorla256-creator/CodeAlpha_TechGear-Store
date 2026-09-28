from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from products.models import Product
from .forms import CheckoutForm
from .models import Order, OrderItem

@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart: messages.info(request, "Your cart is empty."); return redirect("cart:view")
    form = CheckoutForm(request.POST or None, initial={
        "email": request.user.email,
        "full_name": request.user.get_full_name() or request.user.username,
        "payment_method": "cod",
    })
    products = list(Product.objects.filter(id__in=cart, is_active=True))
    if len(products) != len(cart):
        messages.error(request, "A cart item is no longer available. Review your cart before checking out.")
        return redirect("cart:view")
    lines = []
    for product in products:
        try:
            quantity = int(cart.get(str(product.pk), 0))
        except (TypeError, ValueError):
            quantity = 0
        if quantity < 1 or quantity > product.stock:
            messages.error(request, f"Update the quantity for {product.name}; only {product.stock} units are available.")
            return redirect("cart:view")
        lines.append({"product": product, "quantity": quantity, "line_total": product.current_price * quantity})
    subtotal = sum((line["line_total"] for line in lines), Decimal("0.00"))
    shipping = Decimal("0.00") if subtotal >= Decimal("2000.00") else Decimal("99.00")
    total = subtotal + shipping
    free_delivery_gap = max(Decimal("0.00"), Decimal("2000.00") - subtotal)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            product_ids = [line["product"].pk for line in lines]
            locked = {p.pk:p for p in Product.objects.select_for_update().filter(pk__in=product_ids)}
            if any(
                product.pk not in locked
                or line["quantity"] < 1
                or locked[product.pk].stock < line["quantity"]
                or not locked[product.pk].is_active
                for line in lines
                for product in [line["product"]]
            ):
                messages.error(request, "A cart item is no longer available in the requested quantity.")
                return redirect("cart:view")
            subtotal = sum((locked[line["product"].pk].current_price * line["quantity"] for line in lines), Decimal("0.00"))
            shipping = Decimal("0.00") if subtotal >= Decimal("2000.00") else Decimal("99.00")
            order = form.save(commit=False)
            order.user = request.user
            order.total = subtotal + shipping
            order.save()
            for line in lines:
                current = locked[line["product"].pk]
                OrderItem.objects.create(
                    order=order,
                    product=current,
                    product_name=current.name,
                    unit_price=current.current_price,
                    quantity=line["quantity"],
                )
                current.stock -= line["quantity"]
                current.save(update_fields=["stock"])
        request.session["cart"] = {}
        if order.payment_method != "cod":
            return redirect("orders:payment", order_id=order.pk)
        messages.success(request, "Order placed successfully. Pay on delivery.")
        return redirect("orders:success", order_id=order.pk)
    return render(request, "orders/checkout.html", {
        "form": form, "items": lines, "subtotal": subtotal, "shipping": shipping,
        "total": total, "free_delivery_gap": free_delivery_gap,
    })

@login_required
@require_http_methods(["GET", "POST"])
def payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.payment_method == "cod" or order.payment_status != "pending":
        return redirect("orders:detail", order_id=order.pk)
    if request.method == "POST":
        action = request.POST.get("action")
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(), pk=order_id, user=request.user,
            )
            if order.payment_method == "cod" or order.payment_status != "pending" or order.status != "pending":
                messages.error(request, "This payment session is no longer active.")
                return redirect("orders:detail", order_id=order.pk)
            if action == "complete_demo":
                order.payment_status = "paid"
                order.status = "processing"
                order.save(update_fields=["payment_status", "status"])
            elif action == "cancel":
                for item in order.items.select_related("product"):
                    if item.product_id:
                        Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
                order.payment_status = "failed"
                order.status = "cancelled"
                order.save(update_fields=["payment_status", "status"])
            else:
                messages.error(request, "Choose a valid payment action.")
                return redirect("orders:payment", order_id=order.pk)
        if action == "complete_demo":
            messages.success(request, "Demo payment completed. No real payment was collected.")
            return redirect("orders:success", order_id=order.pk)
        messages.info(request, "Payment cancelled. Your order was cancelled and stock was restored.")
        return redirect("orders:detail", order_id=order.pk)
    return render(request, "orders/payment.html", {"order": order})

@login_required
def success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order":order})

@login_required
def history(request):
    return render(request, "orders/order_history.html", {"orders":Order.objects.filter(user=request.user)})

@login_required
def detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order":order})
