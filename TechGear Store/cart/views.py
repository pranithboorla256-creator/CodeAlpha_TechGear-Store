from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from products.models import Product

def cart_page(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart, is_active=True)
    items = []
    for p in products:
        qty = int(cart.get(str(p.pk), 0))
        items.append({"product":p, "quantity":qty, "line_total":p.current_price * qty})
    total = sum((item["line_total"] for item in items), Decimal("0.00"))
    return render(request, "cart/cart.html", {"items":items, "total":total})

@require_POST
def add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    added = False
    try: quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError): quantity = 0
    if quantity < 1: messages.error(request, "Choose a valid quantity.")
    elif product.stock == 0: messages.error(request, "Product is out of stock.")
    else:
        cart = request.session.get("cart", {})
        total = int(cart.get(str(product.pk), 0)) + quantity
        if total > product.stock: messages.error(request, f"Only {product.stock} units are available.")
        else:
            cart[str(product.pk)] = total; request.session["cart"] = cart
            messages.success(request, "Product added to cart successfully.")
            added = True
    if request.POST.get("buy_now") and added:
        return redirect("orders:checkout")
    return redirect(request.POST.get("next") or "cart:view")

@require_POST
def update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try: quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError): quantity = 0
    cart = request.session.get("cart", {})
    if quantity < 1: cart.pop(str(product_id), None); messages.success(request, "Product removed from cart.")
    elif quantity > product.stock: messages.error(request, f"Only {product.stock} units are available.")
    else: cart[str(product_id)] = quantity; messages.success(request, "Cart updated successfully.")
    request.session["cart"] = cart
    return redirect("cart:view")

@require_POST
def remove(request, product_id):
    cart = request.session.get("cart", {}); cart.pop(str(product_id), None)
    request.session["cart"] = cart; messages.success(request, "Product removed from cart.")
    return redirect("cart:view")
