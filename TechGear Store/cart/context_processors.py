def cart_count(request):
    items = request.session.get("cart", {})
    return {"cart_count": sum(max(0, int(q)) for q in items.values())}
