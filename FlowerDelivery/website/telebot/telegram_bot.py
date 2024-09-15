import asyncio
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from .config import TOKEN
from ..models import BotConfig


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_id = update.effective_chat.id  # Получаем chat_id
    # print(f'Подключился пользователь с ID: {bot_id}')  # Выводим chat_id в консоль
    await update.message.reply_text('Сообщения с сайта будут приходить сюда.')
    # Сохраняем ID бота в базу данных асинхронно
    await sync_to_async(BotConfig.objects.update_or_create)(
        id=1, defaults={'bot_id': bot_id}
    )
    # Создаем кнопку "Административная"
    # keyboard = [
    #     [InlineKeyboardButton("Административная", url="https://miponcelbon.beget.app/home_admin/")]
    # ]
    keyboard = [
        [InlineKeyboardButton("Административная", url="127.0.0.1:8000/website/home_admin/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Cтатусами заказа можно управлять на сайте.\nНажмите на кнопку ниже:',
        reply_markup=reply_markup)


def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()


async def send_initial_message(message: str) -> None:
    # Получаем ID бота из базы данных асинхронно
    bot_config = await sync_to_async(BotConfig.objects.first)()
    try:
        id_bot = bot_config.bot_id
        app = ApplicationBuilder().token(TOKEN).build()
        await app.bot.send_message(chat_id=id_bot, text=message)
    except Exception:
        print('Бот ID не найден.')
