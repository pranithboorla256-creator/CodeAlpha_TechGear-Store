from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from products.views import home

handler404 = "products.views.not_found"
urlpatterns = [
    path("admin/", admin.site.urls), path("", home, name="home"),
    path("products/", include("products.urls")), path("accounts/", include("accounts.urls")),
    path("cart/", include("cart.urls")), path("orders/", include("orders.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
