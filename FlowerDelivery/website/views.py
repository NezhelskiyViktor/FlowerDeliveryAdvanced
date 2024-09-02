import pytz
import json
import asyncio
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from .forms import UserRegistrationForm, LoginForm
from .models import Customer, Product, Cart, CartItem, OrderHistory
from .telebot.telegram_bot import send_initial_message


TIME = (8, 23)  # время работы с 8:00 до 23:00
IS_OPEN = False


# Функция для отображения главной страницы
@never_cache
def home(request):
    global TIME

    local_time = timezone.now().astimezone(pytz.timezone('Europe/Moscow'))

    # Установим время начала и окончания работы
    start_time = local_time.replace(hour=TIME[0], minute=0, second=0, microsecond=0)
    end_time = local_time.replace(hour=TIME[1], minute=0, second=0, microsecond=0)

    global IS_OPEN
    IS_OPEN = start_time <= local_time <= end_time

    # Для отладки:
    # IS_OPEN = False
    # request.session.pop('email', None)
    # request.session.pop('buyer', None)
    # request.session.pop('selected_products', None)
    # request.session.pop('cart_id', None)

    try:
        buyer = request.session['buyer']
        customer = get_object_or_404(Customer, name=buyer)
        carts = Cart.objects.filter(customer=customer)
        # Получаем все заказы, связанные с корзинами покупателем
        orders = OrderHistory.objects.filter(cart__in=carts)
        k_orders = orders.count()
    except KeyError:
        buyer = None
        k_orders = 0

    context = {
        'user': buyer,
        'k_orders': k_orders,
        'current_time': local_time.strftime('%H:%M'),
        'open': str(TIME[0]),
        'close': str(TIME[1]),
        'is_open': IS_OPEN
    }
    return render(request, 'website/home.html', context)


def login_view(request):
    try:
        email = request.session['email']
        customer = get_object_or_404(Customer, email=email)  # Поиск пользователя по email
    except KeyError:
        customer = None

    if customer:  # Если пользователь уже зарегистривовался
        return redirect('showcase')

    if request.method == 'POST':
        email = request.POST.get('email')

        if 'login' in request.POST:
            # Обработка формы входа
            try:
                customer = get_object_or_404(Customer, email=email)  # Поиск пользователя по email
                request.session['email'] = email  # запомнить email в сессии
                request.session['buyer'] = customer.name  # запомнить имя пользователя в сессии
                return redirect('showcase')  # переход на страницу витрины
            except:  # Не удалось найти заказчика
                content = {
                    'open': str(TIME[0]),
                    'close': str(TIME[1]),
                    'email': email,
                    'error_login': 'Пользователь с таким E-mail не зарегистрирован.Пожалуйста зарегистрируйтесь.'
                }
                # Возвращаемся на страницу входа
                return render(request, 'website/login.html', content)

        elif 'register' in request.POST:
            # Обработка формы регистрации
            try:
                customer = get_object_or_404(Customer, email=email)  # Поиск пользователя по email
                request.session['email'] = email  # запомнить email в сессии
                request.session['buyer'] = customer.name  # запомнить имя пользователя в сессии
            except:
                form = UserRegistrationForm(request.POST)
                if form.is_valid():  # Проверка формы
                    form.save()  # Сохранение формы
                    request.session['email'] = form.cleaned_data['email']  # запомнить email в сессии
                    request.session['buyer'] = form.cleaned_data['name']  # запомнить имя пользователя в сессии
            return redirect('showcase')  # переход на страницу витрины

    content = {
        'open': str(TIME[0]),
        'close': str(TIME[1]),
        'email': '',
        'error_login': ''
    }
    return render(request, 'website/login.html', content)


# Функция для выхода
def logout_view(request):
    # Очистить конкретные данные
    request.session.pop('email', None)
    request.session.pop('buyer', None)
    request.session.pop('selected_products', None)
    request.session.pop('cart_id', None)
    return redirect('home')  # перенаправление на домашнюю страницу


# Функция для отображения страницы витрины
@never_cache
def showcase(request):
    buyer = request.session.get('buyer')
    if buyer:
        customer = get_object_or_404(Customer, name=buyer)
        delivery_address = customer.delivery_address
    else:
        delivery_address = None

    products = Product.objects.all()

    if buyer and request.method == 'POST':
        product_counts = {key.split('[')[1][:-1]: value for key, value in request.POST.items() if
                          key.startswith('product_counts')}
        total_price = 0
        valid_products = {}

        for product_id, count_str in product_counts.items():
            if count_str.strip().isdigit():
                count = int(count_str)
                if count > 0:
                    product = get_object_or_404(Product, id=int(product_id))
                    total_price += product.price * count
                    valid_products[product] = count

        if total_price > 0:
            new_cart = Cart.objects.create(
                customer=customer,
                delivery_address=delivery_address,
                comment='',
                total_price=total_price,
                created_at=timezone.now().astimezone(pytz.timezone('Europe/Moscow'))
            )

            CartItem.objects.bulk_create([
                CartItem(cart=new_cart, product=product, quantity=count) for product, count in valid_products.items()
            ])

            request.session['cart_id'] = new_cart.id
            return redirect('cart')  # Перенаправляем на страницу просмотра корзины заказчика

        return redirect('home')  # Перенаправляем на главную страницу когда корзина пуста

    context = {
        'products': products,
        'user': buyer,
        'open': str(TIME[0]),
        'close': str(TIME[1]),
        'is_open': IS_OPEN
    }
    return render(request, 'website/showcase.html', context)


# Функция для отображения страницы заказанной корзины
def cart(request):
    carta = get_object_or_404(Cart, id=request.session.get('cart_id'))

    if carta is not None and request.method == 'POST':
        carta.delivery_address = request.POST.get('delivery_address')
        carta.comment = request.POST.get('comment')
        carta.save()  # Сохраняем обновленный адрес доставки и комментарии
        now_is = timezone.now().astimezone(pytz.timezone('Europe/Moscow'))
        new_order = OrderHistory.objects.create(
            cart=carta,
            order_date=now_is,
            cart_price=carta.total_price
        )
        new_order.save()

        buket = carta.get_items_display()
        text_for_bot = (f'{now_is.strftime("%H:%M %d.%m.%y")}\n{new_order}\n'
                        f'Букет: {buket}\n'
                        f'Сумма заказа: {new_order.cart_price}₽\n'
                        f'Адрес доставки: {carta.delivery_address}')
        if carta.comment != '':
            text_for_bot += f'\n{carta.comment}'
        # Отпраляем сообщение боту
        asyncio.run(send_initial_message(text_for_bot))

        return redirect('orders')

    # Если request.method == 'GET' то
    context = {
        'cart': carta,
        'open': str(TIME[0]),
        'close': str(TIME[1]),
    }
    return render(request, 'website/cart.html', context)


# Функция для авторизации Админа
def login_admin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_admin')  # Замените 'home' на вашу главную страницу
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'website/login_admin.html')


# Функция для обновления статуса
def update_order_status(request):
    try:
        # Получаем данные из JSON-запроса
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')

        # Находим заказ по ID и обновляем статус
        order = OrderHistory.objects.get(id=order_id)
        order.status = new_status  # Предполагается, что status является полем модели
        order.save()
        text = f'\nСтатус заказа №{order_id} изменен на {order.get_status_display()}.'
        # send_message(text)
        asyncio.run(send_initial_message(text))
        # Возвращаем успешный ответ
        return JsonResponse({'status': 'success', 'new_status': order.get_status_display()})

    except OrderHistory.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Функция для отображения страницы истории заказов
def order_history(request):
    # Проверяем, авторизован ли пользователь
    try:
        buyer = request.session['buyer']
        customer = get_object_or_404(Customer, name=buyer)
        carts = Cart.objects.filter(customer=customer)  # Получаем все корзины покупателя
        # Получаем все заказы, связанные с корзинами покупателя
        orders = OrderHistory.objects.filter(cart__in=carts).order_by('-order_date')

        if request.method == 'POST':
            if 'repeat' in request.POST:  # Обработка нажатия кнопки "Повторить"
                order_id = request.POST.get('repeat')
                order = get_object_or_404(OrderHistory, id=order_id)
                carta = order.cart
                new_cart = Cart.objects.create(
                    customer=customer,
                    delivery_address=carta.delivery_address,
                    comment=carta.comment,
                    total_price=carta.total_price,
                    created_at=timezone.now().astimezone(pytz.timezone('Europe/Moscow'))
                )
                cart_items = carta.items.all()
                # Преобразуем в нужный формат данные из корзины
                products = [(item.product, item.quantity) for item in cart_items]
                # Обрабатываем выбранные продукты
                for product, count in products:
                    product_ = Product.objects.get(id=product.id)
                    # Создаем копию букета корзины
                    cart_item = CartItem.objects.create(cart=new_cart, product=product_, quantity=count)
                    cart_item.save()
                request.session['cart_id'] = new_cart.id
                # Перенаправляем на страницу просмотра созданной копии корзины
                return redirect('cart')
            else:  # Обработка изменения статуса
                update_order_status(request)

        # Если request.method == 'GET' то
        context = {
            'orders': orders,
            'user': buyer,
            'open': str(TIME[0]),
            'close': str(TIME[1]),
            'is_open': IS_OPEN,
        }
        return render(request, 'website/order_history.html', context)
    except KeyError:
        return redirect('login')

# Функция для отображения страницы истории заказов Админу
def home_admin(request):
    # Получаем все корзины
    carts = Cart.objects.all()
    # Получаем все заказы, связанные с корзинами
    orders = OrderHistory.objects.filter(cart__in=carts).order_by('-order_date')

    # Обработка POST-запроса для обновления статуса заказа
    if request.method == 'POST':
        # Обработка изменения статуса
        update_order_status(request)

    # Если это GET-запрос, рендерим шаблон
    return render(request, 'website/home_admin.html', {'orders': orders})


# Страница О нашем сайте
def about(request):
    context = {
        'open': str(TIME[0]),
        'close': str(TIME[1]),
    }
    return render(request, 'website/about.html', context)

