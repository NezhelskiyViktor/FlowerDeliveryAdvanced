from django.test import TestCase
from django.contrib.auth.models import User
from .models import Customer, Product, Cart, CartItem, OrderHistory


class CustomerModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_customer(self):
        customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            phone='1234567890',
            delivery_address='Test Address'
        )
        self.assertEqual(customer.name, 'Test Customer')
        self.assertEqual(customer.email, 'test@example.com')
        self.assertEqual(customer.phone, '1234567890')
        self.assertEqual(customer.delivery_address, 'Test Address')


class ProductModelTests(TestCase):

    def test_create_product(self):
        product = Product.objects.create(
            name='Test Product',
            price=99.99
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 99.99)


class CartModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            phone='1234567890',
            delivery_address='Test Address'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=99.99
        )

    def test_create_cart(self):
        cart = Cart.objects.create(
            customer=self.customer,
            delivery_address='Test Address',
            comment='No comments',
            total_price=199.98,
        )
        self.assertEqual(cart.customer, self.customer)
        self.assertEqual(cart.delivery_address, 'Test Address')
        self.assertEqual(cart.comment, 'No comments')
        self.assertEqual(cart.total_price, 199.98)

    def test_add_item_to_cart(self):
        cart = Cart.objects.create(
            customer=self.customer,
            delivery_address='Test Address',
            comment='No comments',
            total_price=199.98,
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first(), cart_item)
        self.assertEqual(cart.items.first().quantity, 2)


class OrderHistoryModelTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            phone='1234567890',
            delivery_address='Test Address'
        )
        self.cart = Cart.objects.create(
            customer=self.customer,
            delivery_address='Test Address',
            comment='No comments',
            total_price=199.98,
        )

    def test_create_order_history(self):
        order_history = OrderHistory.objects.create(
            cart=self.cart,
            cart_price=self.cart.total_price,
            status='TEST'
        )
        self.assertEqual(order_history.cart, self.cart)
        self.assertEqual(order_history.cart_price, self.cart.total_price)
        self.assertEqual(order_history.status, 'TEST')

