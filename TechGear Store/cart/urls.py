from django.urls import path
from . import views
app_name = "cart"
urlpatterns = [path("", views.cart_page, name="view"), path("add/<int:product_id>/", views.add, name="add"), path("update/<int:product_id>/", views.update, name="update"), path("remove/<int:product_id>/", views.remove, name="remove")]
