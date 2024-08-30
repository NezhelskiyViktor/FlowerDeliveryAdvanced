from django.core.management.base import BaseCommand
from ...telegram_bot import start_bot  # Импортируйте вашу функцию main


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        start_bot()

