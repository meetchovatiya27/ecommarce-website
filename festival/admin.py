from django.contrib import admin
from .models import FestivalSale

@admin.register(FestivalSale)
class FestivalSaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_date', 'end_date', 'discount_percent', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
