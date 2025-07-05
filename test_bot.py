import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8199891784:AAEdB1f6A1UnAq7xUdkGR3aBcmxPomZT3o8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 NEON FREELANCE", url="https://example.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚀 БОТ РАБОТАЕТ!", reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()