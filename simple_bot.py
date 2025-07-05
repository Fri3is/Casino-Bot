#!/usr/bin/env python3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
TOKEN = "8199891784:AAEdB1f6A1UnAq7xUdkGR3aBcmxPomZT3o8"

# Готовая ссылка на фриланс
FREELANCE_LINK = "https://htmlpreview.github.io/?https://gist.githubusercontent.com/anonymous/demo/raw/neon-freelance.html"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    
    text = f"""🚀 NEON FREELANCE ГОТОВ!

Привет, {user.first_name}!

🔥 ТАКОГО ЕЩЁ НИКТО НЕ ДЕЛАЛ!

✨ Неоновый дизайн
💎 4 реальных заказа
🚀 Рабочие кнопки

👇 ЖМИТЕ ССЫЛКУ! 👇"""
    
    keyboard = [[InlineKeyboardButton("🚀 ОТКРЫТЬ NEON FREELANCE", url=FREELANCE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

def main():
    """Запуск бота"""
    print("🚀 Запускаю простого бота...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()