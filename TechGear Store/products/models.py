from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse("products:category", args=[self.slug])

class Product(models.Model):
    name = models.CharField(max_length=180, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    description = models.TextField()
    short_description = models.CharField(max_length=240, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=100, db_index=True)
    model_number = models.CharField(max_length=100, blank=True)
    image = models.CharField(max_length=1000, blank=True, help_text="Direct image URL for this product")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_active", "category"]), models.Index(fields=["is_active", "price"])]
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    @property
    def current_price(self): return self.discount_price if self.discount_price is not None else self.price
    @property
    def on_sale(self): return self.discount_price is not None and self.discount_price < self.price
    def get_absolute_url(self): return reverse("products:detail", args=[self.slug])
    def __str__(self): return self.name
