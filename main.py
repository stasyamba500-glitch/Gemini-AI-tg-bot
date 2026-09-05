import os
import telebot
from telebot import types
from duckduckgo_search import DDGS

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_history = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_search = types.KeyboardButton("Пошук")
    btn_history = types.KeyboardButton("Мої запити")
    markup.add(btn_search, btn_history)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Привіт! Я бот для пошуку в мережі.\nНатисніть Пошук, щоб зробити запит.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "Мої запити")
def show_history(message):
    user_id = message.from_user.id
    history = user_history.get(user_id, [])
    
    if not history:
        bot.send_message(message.chat.id, "Ваша історія запитів порожня.", reply_markup=get_main_keyboard())
    else:
        text = "📜 Ваші останні запити:\n\n"
        for idx, item in enumerate(history[-10:], 1):
            text += f"{idx}. {item}\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "Пошук")
def ask_query(message):
    msg = bot.send_message(message.chat.id, "Введіть ваш пошуковий запит:")
    bot.register_next_step_handler(msg, process_search)

def process_search(message):
    query = message.text
    user_id = message.from_user.id

    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(query)

    bot.send_message(message.chat.id, f"Шукаю: *{query}*...", parse_mode="Markdown")

    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(r)
        
        if not results:
            bot.send_message(message.chat.id, "На жаль, за вашим запитом нічого не знайдено.", reply_markup=get_main_keyboard())
            return

        text = "🔎 Результати пошуку:\n\n"
        for idx, res in enumerate(results, 1):
            text += f"{idx}. [{res['title']}]({res['href']})\n"

        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard(), disable_web_page_preview=True)
    except Exception as e:
        bot.send_message(message.chat.id, f"Сталася помилка при пошуку: {e}", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    process_search(message)

if __name__ == '__main__':
    bot.infinity_polling()
