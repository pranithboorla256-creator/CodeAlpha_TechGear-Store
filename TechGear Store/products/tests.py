from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product
from cart.views import add
from orders.models import Order, OrderItem

class StoreFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Keyboards")
        self.product = Product.objects.create(name="Test Keyboard", category=self.category, description="A test keyboard", brand="Test", price="1000.00", stock=5, slug="test-keyboard")
    def test_product_listing_detail_and_search(self):
        self.assertContains(self.client.get(reverse("products:list")), "Test Keyboard")
        self.assertContains(self.client.get(reverse("products:detail", args=[self.product.slug])), "A test keyboard")
        self.assertContains(self.client.get(reverse("products:list")+"?q=Test"), "Test Keyboard")
        self.assertNotContains(self.client.get(reverse("products:list")+"?q=xyz"), "Test Keyboard")
    def test_registration_login_logout(self):
        response = self.client.post(reverse("accounts:register"), {"username":"gearuser","email":"gear@example.com","password1":"SafePassword123!","password2":"SafePassword123!"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="gearuser").exists())
        self.client.post(reverse("accounts:logout"))
        response = self.client.post(reverse("accounts:login"), {"username":"gearuser","password":"SafePassword123!"})
        self.assertEqual(response.status_code, 302)
    def test_cart_stock_and_updates(self):
        self.assertEqual(self.client.get(reverse("cart:view")).status_code, 200)
        response = self.client.post(reverse("cart:add", args=[self.product.pk]), {"quantity":2})
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)
        self.assertEqual(self.client.get(reverse("cart:view")).status_code, 200)
        self.client.post(reverse("cart:add", args=[self.product.pk]), {"quantity":8})
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)
        self.client.post(reverse("cart:update", args=[self.product.pk]), {"quantity":3})
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 3)
        self.client.post(reverse("cart:remove", args=[self.product.pk]))
        self.assertNotIn(str(self.product.pk), self.client.session["cart"])
    def test_checkout_creates_order_total_and_reduces_stock(self):
        user = User.objects.create_user("buyer", password="SafePassword123!")
        self.client.force_login(user)
        session = self.client.session; session["cart"] = {str(self.product.pk):2}; session.save()
        self.assertEqual(self.client.get(reverse("orders:checkout")).status_code, 200)
        response = self.client.post(reverse("orders:checkout"), {"full_name":"Test Buyer","email":"buyer@example.com","phone":"9876543210","address":"1 Test Street","city":"Pune","postal_code":"411001","payment_method":"cod"})
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=user)
        self.assertEqual(order.total, 2000)
        self.assertEqual(OrderItem.objects.get(order=order).quantity, 2)
        self.product.refresh_from_db(); self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.client.get(reverse("orders:history")).status_code, 200)
        self.assertEqual(self.client.get(reverse("orders:detail", args=[order.pk])).status_code, 200)
