from django.contrib import admin
from .models import Product, Review, Order, OrderItem, Shipping, Promotion


class PromotionInline(admin.TabularInline):
    model = Promotion
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'skin_type', 'price', 'is_active')
    inlines = [PromotionInline]


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'discount_percent',
        'is_active',
        'start_date',
        'end_date',
        'discounted_price_display',
    )
    list_filter = ('is_active', 'discount_percent')
    search_fields = ('product__name',)

    def discounted_price_display(self, obj):
        return f"{obj.discounted_price():.2f} MKD"

    discounted_price_display.short_description = "Discounted price"


admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Shipping)
