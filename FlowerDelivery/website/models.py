from django.db import models
from django.urls import reverse


# 1. Заказчики
class Customer(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=100)
    email = models.EmailField(verbose_name='Электронная почта', unique=True)
    phone = models.CharField(verbose_name='Телефон', max_length=20, blank=True, null=True)
    delivery_address = models.TextField(verbose_name='Адрес' )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'заказчик'
        verbose_name_plural = 'Заказчики'


# 2. Продукты
class Product(models.Model):
    name = models.CharField(verbose_name='Цветок', max_length=200)
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)
    image = models.ImageField(verbose_name='Изображение', upload_to='static/website/img/')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'цветок'
        verbose_name_plural = 'Цветы'


# 3. Корзина заказчика
class Cart(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='Заказчик', on_delete=models.CASCADE)
    delivery_address = models.TextField(verbose_name='Адрес')
    comment = models.TextField(verbose_name='Комментарии', blank=True, null=True)
    total_price = models.DecimalField(verbose_name='Стоимость', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(verbose_name='Дата', auto_now_add=True)

    def __str__(self):
        return f"№{self.id}"

    def get_items_display(self):
        return ', '.join([f"{item.product.name}: {item.quantity} шт." for item in self.items.all()])

    get_items_display.short_description = 'В корзине'

    class Meta:
        verbose_name = 'корзинн'
        verbose_name_plural = 'Корзины заказов'


# 3.1. Товары в корзине
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name='Корзина',  related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Цветок в корзине',  on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f"{self.product.name}: {self.quantity} шт."

    class Meta:
        verbose_name = 'цветок в корзине'
        verbose_name_plural = 'Цветы в корзинах'


# 4. История заказов
class OrderHistory(models.Model):
    STATUS_CHOICES = [
        ('ORDERED', 'Заказан'),
        ('RECEIVED', 'Получен'),
        ('CANCELED', 'Отменен'),
        ('PAID', 'Оплачен'),
    ]
    USER_CHOICES = [
        ('ORDERED', 'Заказан'),
        ('RECEIVED', 'Получен'),
        ('CANCELED', 'Отменен'),
    ]

    cart = models.OneToOneField(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    order_date = models.DateTimeField(verbose_name='Дата заказа', auto_now_add=True)
    cart_price = models.DecimalField(verbose_name='Стоит руб.', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Статус', max_length=10, choices=STATUS_CHOICES, default='ORDERED')

    def __str__(self):
        return f"Заказ {self.id} - {self.cart.customer.name}"

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'


class BotConfig(models.Model):
    bot_id = models.CharField(max_length=16, verbose_name='ID бота')
