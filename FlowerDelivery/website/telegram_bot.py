import asyncio
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from .telebot.config import TOKEN
from .models import BotConfig


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_id = update.effective_chat.id  # Получаем chat_id
    print(f'Подключился пользователь с ID: {bot_id}')  # Выводим chat_id в консоль
    await update.message.reply_text('Сообщения с сайта будут приходить сюда.')
    # Сохраняем ID бота в базу данных асинхронно
    await sync_to_async(BotConfig.objects.update_or_create)(
        id=1, defaults={'bot_id': bot_id}
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('?')


def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()


async def send_initial_message(message: str) -> None:
    # Получаем ID бота из базы данных асинхронно
    bot_config = await sync_to_async(BotConfig.objects.first)()
    if bot_config:
        id_bot = bot_config.bot_id
        app = ApplicationBuilder().token(TOKEN).build()
        if id_bot:
            print(f'Это Chat ID: {id_bot}')  # Выводим id_bot в консоль
            try:
                await app.bot.send_message(chat_id=id_bot, text=message)
            except Exception as e:
                print(f'Ошибка отправки сообщения: {e}')
    else:
        print('Бот ID не найден.')
