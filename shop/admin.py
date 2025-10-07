from django.contrib import admin
from .models import Category, Product, About, Contact, Cart, CartItem, HomepageAnimation, StaticPage

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

@admin.register(HomepageAnimation)
class HomepageAnimationAdmin(admin.ModelAdmin):
    list_display = ("title", "animation_code")
    search_fields = ("title",)

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




