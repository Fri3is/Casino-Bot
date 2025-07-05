#!/bin/bash

echo "🚀 Запуск FreelanceBot..."
cd /workspace
source venv/bin/activate
echo "🔧 Активировано виртуальное окружение"
echo "📝 Проверка зависимостей..."
pip list | grep python-telegram-bot
echo "🚀 Запуск бота..."
python bot.py