from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import pandas as pd
import datetime

# Токен из BotFather
TOKEN = '7293266241:AAHf82BsRaqUBwZuWQwIbTEqHAesAABIJyk'

# Порог скоринга для одобрения
SCORING_THRESHOLD = 700

# Функция сохранения заявки
def save_application(name, phone, amount, income, purpose):
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Дата", "ЗаявкаID", "ТипКредита", "Сумма", "Доход", "Скоринг",
            "ВремяОбработки", "Одобрено", "Имя", "Телефон", "Цель"
        ])

    # Рассчитываем скоринг и статус одобрения
    scoring = int(float(income) * 0.1 + float(amount) / 10000)
    approved = 1 if scoring >= SCORING_THRESHOLD else 0

    # Новый ID заявки
    next_id = 1 if df.empty else df['ЗаявкаID'].max() + 1

    new_entry = {
        "Дата": datetime.datetime.now().strftime("%Y-%m-%d"),
        "ЗаявкаID": next_id,
        "ТипКредита": "Автокредит",
        "Сумма": amount,
        "Доход": income,
        "Скоринг": scoring,
        "ВремяОбработки": 1,
        "Одобрено": approved,
        "Имя": name,
        "Телефон": phone,
        "Цель": purpose
    }

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv("data.csv", index=False)

    print("Заявка сохранена:", new_entry)

    return approved  # Возвращаем статус одобрения


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Подать заявку на кредит", callback_data='apply')],
        [InlineKeyboardButton("Открыть дашборд", url="https://yourusername.pythonanywhere.com")]   # 🔗 Ссылка на дашборд
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
        await update.message.reply_text("Каков ваш ежемесячный доход?")
        context.user_data['step'] = 'income'

    elif step == 'income':
        context.user_data['income'] = update.message.text
        await update.message.reply_text("На какую цель вы берете кредит? Например: покупка авто.")
        context.user_data['step'] = 'purpose'

    elif step == 'purpose':
        context.user_data['purpose'] = update.message.text

        # Получаем данные из контекста
        name = context.user_data.get('name')
        phone = context.user_data.get('phone')
        amount = context.user_data.get('amount')
        income = context.user_data.get('income')
        purpose = context.user_data.get('purpose')

        # Сохранение заявки
        approved = save_application(name, phone, amount, income, purpose)

        # Сообщение пользователю
        if approved:
            msg = "✅ Ваша заявка одобрена!"
        else:
            msg = "❌ К сожалению, заявка не прошла скоринг."

        await update.message.reply_text(msg)

        # Кнопка дашборда
        keyboard = [[InlineKeyboardButton("📊 Открыть дашборд", url="http://127.0.0.1:8050/")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Вы можете посмотреть статистику здесь:", reply_markup=reply_markup)

        # Сброс шагов
        context.user_data.clear()


# Основная функция
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()