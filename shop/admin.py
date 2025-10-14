from django.contrib import admin
from .models import Category, Product, About, Contact, Cart, CartItem, StaticPage, Order, OrderItem, UserPurchaseHistory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id',"name", "description")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id',"name", "category", "price", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "subtitle", "short_description")} ),
        ("Content", {"fields": ("content", "mission", "vision", "shop_details")} ),
        ("Images", {"fields": ("image", "hero_image")} ),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",), "description": "Read-only timestamps"}),
    )
    readonly_fields = ("created_at", "updated_at")

admin.site.register(Contact)
admin.site.register(Cart)
admin.site.register(CartItem)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at", "external_url")
    list_editable = ("slug",)
    search_fields = ("title", "content", "external_url")
    fieldsets = (
        (None, {"fields": ("title", "slug")} ),
        ("Content", {"fields": ("content",)} ),
        ("External", {"fields": ("external_url",), "description": "Optional: redirect to an external policy URL."}),
    )


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


@admin.register(UserPurchaseHistory)
class UserPurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'order', 'quantity', 'purchased_at')
    list_filter = ('purchased_at',)
    search_fields = ('user__username', 'product__name', 'order__id')
