from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, About, Contact, Cart, CartItem, StaticPage, Order, OrderItem, UserPurchaseHistory

# ---------------- CATEGORY ---------------- #
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', "name", "description")
    search_fields = ("name",)

# ---------------- PRODUCT ---------------- #
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'available', 'discount_percent', 'description_short', 'image_tag', 'created_at')
    list_filter = ('category', 'available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('name', 'price', 'stock', 'available', 'discount_percent')
    readonly_fields = ('image_tag',)

    # Small image preview
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px; height:auto;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

    # Show a shortened description to save space
    def description_short(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

    # Reduce row spacing using CSS
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

# ---------------- ABOUT ---------------- #
@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "subtitle", "short_description")}),
        ("Content", {"fields": ("content", "mission", "vision", "shop_details")}),
        ("Images", {"fields": ("image", "hero_image")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",), "description": "Read-only timestamps"}),
    )
    readonly_fields = ("created_at", "updated_at")

# ---------------- CONTACT ---------------- #
admin.site.register(Contact)

# ---------------- CART ---------------- #
admin.site.register(Cart)
admin.site.register(CartItem)

# ---------------- STATIC PAGE ---------------- #
@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at", "external_url")
    list_editable = ("slug",)
    search_fields = ("title", "content", "external_url")
    fieldsets = (
        (None, {"fields": ("title", "slug")}),
        ("Content", {"fields": ("content",)}),
        ("External", {"fields": ("external_url",), "description": "Optional: redirect to an external policy URL."}),
    )

# ---------------- ORDER & ORDER ITEMS ---------------- #
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'product', 'quantity', 'price', 'subtotal')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'mobile', 'city', 'status', 'amount', 'created_at')
    search_fields = ('user__username', 'name', 'mobile', 'city')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

# ---------------- USER PURCHASE HISTORY ---------------- #
@admin.register(UserPurchaseHistory)
class UserPurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'order', 'quantity', 'purchased_at')
    list_filter = ('purchased_at',)
    search_fields = ('user__username', 'product__name', 'order__id')
