# Это старый вариант отправки сообщений с помощью бота ID которого записан в config.py
import requests
from .config import TOKEN, BOT_ID


def send_message(text):
    base_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': BOT_ID,
        'text': text
    }

    response = requests.post(base_url, json=payload)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    return response.json()
