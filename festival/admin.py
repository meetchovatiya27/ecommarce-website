from django.contrib import admin
from .models import FestivalSale

@admin.register(FestivalSale)
class FestivalSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
