from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


# ---------------- CATEGORY & PRODUCT ---------------- #
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/%Y/%m', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    discount_percent = models.PositiveIntegerField(default=0, help_text="Percentage discount for sale items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


# ---------------- ABOUT & STATIC PAGE ---------------- #
class About(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    short_description = models.TextField(blank=True)
    content = models.TextField()
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    shop_details = models.TextField(blank=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='about/hero/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']


class StaticPage(models.Model):
    SLUG_CHOICES = (
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms & Conditions'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True, choices=SLUG_CHOICES)
    content = models.TextField()
    external_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['slug']


# ---------------- CONTACT ---------------- #
class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        ordering = ['-created_at']


# ---------------- CART SYSTEM ---------------- #
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Cart - {username}"

    class Meta:
        ordering = ['-updated_at']


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    class Meta:
        unique_together = ('cart', 'product')


# ---------------- ORDER SYSTEM ---------------- #
def generate_unique_order_number():
    """
    Generates a unique 12-character order number for each order.
    """
    while True:
        new_order_number = uuid.uuid4().hex[:12].upper()
        from django.apps import apps
        Order = apps.get_model('shop', 'Order')  # avoids circular import
        if not Order.objects.filter(order_number=new_order_number).exists():
            return new_order_number


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='Anonymous')
    mobile = models.CharField(max_length=20, default='0000000000')
    city = models.CharField(max_length=100, default='Unknown')
    address = models.TextField(default='Not provided')
    pincode = models.CharField(max_length=10, default="")

    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Fixed: Using default callable instead of None
    order_number = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        default=generate_unique_order_number,
        blank=False
    )

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


# ---------------- USER PURCHASE HISTORY ---------------- #
class UserPurchaseHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{self.user.username} - {product_name} ({self.purchased_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name_plural = "User Purchase Histories"
        ordering = ['-purchased_at']

        