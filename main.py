import os
import telebot
from telebot import types
from googlesearch import search

# Отримання токена з змінних оточення
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Словник для збереження історії пошуків (user_id: [список запитів])
user_history = {}

# Створення клавіатури з кнопками
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
        "Привіт! Я бот для пошуку в Google.\nНатисніть Пошук, щоб зробити запит, або Мої запити, щоб переглянути історію.",
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

    # Зі збереженням історії
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(query)

    bot.send_message(message.chat.id, f"Шукаю в Google: *{query}*...", parse_mode="Markdown")

    try:
        # Отримання перших 5 результатів пошуку
        results = list(search(query, num_results=5, lang="uk"))
        
        if not results:
            bot.send_message(message.chat.id, "На жаль, за вашим запитом нічого не знайдено.", reply_markup=get_main_keyboard())
            return

        text = "🔎 Результати пошуку:\n\n"
        for idx, link in enumerate(results, 1):
            text += f"{idx}. {link}\n"

        bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Сталася помилка при пошуку: {e}", reply_markup=get_main_keyboard())

# Решта текстових повідомлень, які не натиснуті через кнопки
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    process_search(message)

if __name__ == '__main__':
    bot.infinity_polling()
