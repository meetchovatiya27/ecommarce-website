from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
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
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        upload_to='products/%Y/%m',
        help_text='Upload product image'
    )
    category = models.ForeignKey(
        Category, 
        related_name='products',
        on_delete=models.CASCADE
    )
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


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

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity


class HomepageAnimation(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='animations/')
    animation_code = models.TextField(help_text="Paste animation code (e.g. JavaScript/CSS)")

    def __str__(self):
        return self.title
     
