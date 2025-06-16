from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import pandas as pd
import datetime

# Токен из BotFather
TOKEN = '7293266241:AAHf82BsRaqUBwZuWQwIbTEqHAesAABIJyk'

# Функция сохранения заявки в CSV
# Функция сохранения заявки с типом "Автокредит"
def save_application(name, phone, amount, purpose):
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Дата", "Имя", "Телефон", "ТипКредита", "Сумма", "Цель"])

    new_entry = {
        "Дата": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Имя": name,
        "Телефон": phone,
        "ТипКредита": "Автокредит",  # Всегда Автокредит
        "Сумма": amount,
        "Цель": purpose
    }

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv("data.csv", index=False)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Подать заявку на кредит", callback_data='apply')],
        [InlineKeyboardButton("Открыть дашборд", url="https://yourusername.pythonanywhere.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Здравствуйте! Я помогу вам подать заявку на кредит.', reply_markup=reply_markup)


# Обработка нажатия кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'apply':
        await query.edit_message_text(text="Пожалуйста, укажите ваше имя:")
        context.user_data['step'] = 'name'
    elif query.data == 'open_dashboard':
        await query.edit_message_text(text="Нажмите кнопку ниже, чтобы открыть дашборд.")


# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')

    if step == 'name':
        context.user_data['name'] = update.message.text
        await update.message.reply_text("Укажите ваш номер телефона:")
        context.user_data['step'] = 'phone'

    elif step == 'phone':
        context.user_data['phone'] = update.message.text
        await update.message.reply_text("Какую сумму вы хотите получить?")
        context.user_data['step'] = 'amount'

    elif step == 'amount':
        context.user_data['amount'] = update.message.text
        await update.message.reply_text("На какую цель вы берете кредит? Например: ремонт, покупка авто и т.п.")
        context.user_data['step'] = 'purpose'

    elif step == 'purpose':
        context.user_data['purpose'] = update.message.text

        # Сохранение данных
        name = context.user_data.get('name')
        phone = context.user_data.get('phone')
        amount = context.user_data.get('amount')
        purpose = context.user_data.get('purpose')

        save_application(name, phone, amount, purpose)

        await update.message.reply_text("Спасибо! Ваша заявка принята. Мы свяжемся с вами.")

        # Кнопка для дашборда
        keyboard = [[InlineKeyboardButton("Открыть дашборд", url="http://127.0.0.1:8050/")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Вы можете посмотреть аналитику здесь:", reply_markup=reply_markup)

        context.user_data.clear()


# Основная функция
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()