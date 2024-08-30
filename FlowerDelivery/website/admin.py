from django.contrib import admin
from .models import Customer, Product, Cart, CartItem, OrderHistory, BotConfig


@admin.register(Customer)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'delivery_address')
    search_fields = ('name', 'email', 'phone', 'delivery_address')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'image')
    search_fields = ('name', 'price')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'delivery_address', 'comment', 'total_price', 'created_at', 'get_items_display')
    search_fields = ('customer__name', 'comment', 'total_price', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('cart__customer__name', 'product__name', 'quantity')


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_customer_name', 'cart', 'order_date', 'cart_price', 'status', 'get_products')
    search_fields = ('cart__customer__name', 'order_date', 'cart_price', 'status', 'cart__items__product__name')

    def get_customer_name(self, obj):
        return obj.cart.customer.name
    get_customer_name.short_description = 'Заказчик'

    def get_products(self, obj):
        return ", ".join([f"{item.product.name}: {item.quantity} шт." for item in obj.cart.items.all()])
    get_products.short_description = 'Букеты'


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_id')
    search_fields = ('bot_id',)
