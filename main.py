import os
import telebot
from telebot import types
from google import genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")

user_history = {}


def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Пошук"), types.KeyboardButton("Мої запити")
    )
    return markup


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я готов к работе. Выберите действие:",
        reply_markup=main_keyboard(),
    )


@bot.message_handler(func=lambda message: message.text == "Мої запити")
def show_history(message):
    user_id = message.from_user.id
    history = user_history.get(user_id, [])

    if history:
        response = "Ваши последние запросы:\n\n" + "\n".join(history)
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Вы еще не делали запросов.")


@bot.message_handler(
    func=lambda message: message.text not in ["Пошук", "Мої запити"]
)
def handle_query(message):
    user_id = message.from_user.id
    query = message.text

    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(query)

    try:
        response = chat.send_message(query)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке запроса.")


@bot.message_handler(func=lambda message: message.text == "Пошук")
def start_search(message):
    bot.reply_to(message, "Просто отправьте ваш вопрос в чат.")


if name == "main":
    bot.infinity_polling()
