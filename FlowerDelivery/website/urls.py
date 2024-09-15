from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('about/', views.about, name='about'),  # О нашем сайте
    path('login/', views.login_view, name='login'),  # Страница входа
    path('logout/', views.logout_view, name='logout'),  # Функция для выхода
    path('showcase/', views.showcase, name='showcase'),  # Страница витрины/каталога для заказчиков
    path('cart/', views.cart, name='cart'),  # Страница корзины для заказа
    path('orders/', views.order_history, name='orders'),  # Страница истории заказов
    path('home_admin/', views.home_admin, name='home_admin'),  # Страница администратора
]
