from django.urls import path
from . import views
app_name = "orders"
urlpatterns = [path("checkout/", views.checkout, name="checkout"), path("payment/<int:order_id>/", views.payment, name="payment"), path("success/<int:order_id>/", views.success, name="success"), path("history/", views.history, name="history"), path("<int:order_id>/", views.detail, name="detail")]
