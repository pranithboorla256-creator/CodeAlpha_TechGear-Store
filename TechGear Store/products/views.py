from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from .models import Category, Product

def home(request):
    return render(request, "home.html", {"categories": Category.objects.all(), "featured": Product.objects.filter(is_active=True, is_featured=True)[:8], "deals": Product.objects.filter(is_active=True, discount_price__isnull=False)[:4]})

def product_list(request, category_slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    query = request.GET.get("q", "").strip()
    if query: products = products.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(category__name__icontains=query) | Q(description__icontains=query))
    if request.GET.get("brand"): products = products.filter(brand__iexact=request.GET["brand"])
    if request.GET.get("min_price"): products = products.filter(price__gte=request.GET["min_price"])
    if request.GET.get("max_price"): products = products.filter(price__lte=request.GET["max_price"])
    ordering = {"price_asc":"price", "price_desc":"-price", "rating":"-rating", "name":"name", "newest":"-created_at"}.get(request.GET.get("sort"), "-created_at")
    page = Paginator(products.order_by(ordering), 12).get_page(request.GET.get("page"))
    return render(request, "products/product_list.html", {"page":page, "products":page.object_list, "category":category, "query":query, "categories":Category.objects.all(), "brands":Product.objects.filter(is_active=True).values_list("brand", flat=True).distinct().order_by("brand")})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "products/product_detail.html", {"product":product, "related":related})

def not_found(request, exception):
    return render(request, "404.html", status=404)
