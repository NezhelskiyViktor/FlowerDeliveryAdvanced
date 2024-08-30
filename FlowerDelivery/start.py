import threading
import os


def runserver():
    os.system("python manage.py runserver")


def start_bot():
    os.system("python manage.py start_bot")


if __name__ == "__main__":
    # Создаем потоки
    server_thread = threading.Thread(target=runserver)
    bot_thread = threading.Thread(target=start_bot)

    # Запускаем потоки
    try:
        server_thread.start()
        bot_thread.start()
        # и ждем, пока они завершат работу
        server_thread.join()
        bot_thread.join()
    except KeyboardInterrupt:
        print("Программа остановлена пользователем.")