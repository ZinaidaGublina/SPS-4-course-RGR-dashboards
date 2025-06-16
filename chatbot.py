from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import CallbackQueryHandler

# Токен из BotFather
TOKEN = '7293266241:AAHf82BsRaqUBwZuWQwIbTEqHAesAABIJyk'


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Подать заявку на кредит", callback_data='apply')]]
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
        await update.message.reply_text("Спасибо! Ваша заявка принята. Мы свяжемся с вами.")
        context.user_data.clear()


# Основная функция
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрация хэндлеров
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()