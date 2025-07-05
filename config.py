import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Settings
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
PORT = int(os.getenv('PORT', 8000))

# Database Settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///freelance_bot.db')

# Redis Settings (for caching)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Admin Settings
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Bot Settings
MAX_ORDERS_PER_USER = 10
MAX_BIDS_PER_ORDER = 50
MIN_RATING = 1
MAX_RATING = 5
COMMISSION_RATE = 0.05  # 5% комиссия

# File Upload Settings
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip', '.rar'}

# Categories
CATEGORIES = [
    "🖥️ Программирование",
    "🎨 Дизайн",
    "📝 Копирайтинг",
    "📊 Маркетинг",
    "🔊 Аудио/Видео",
    "🌐 Веб-разработка",
    "📱 Мобильная разработка",
    "🤖 AI/ML",
    "📚 Переводы",
    "🔧 Другое"
]

# Статусы заказов
ORDER_STATUS = {
    'ACTIVE': 'Активный',
    'IN_PROGRESS': 'В работе',
    'COMPLETED': 'Завершен',
    'CANCELLED': 'Отменен',
    'DISPUTE': 'Спор'
}

# Типы пользователей
USER_TYPES = {
    'CLIENT': 'Заказчик',
    'FREELANCER': 'Исполнитель',
    'BOTH': 'Заказчик и Исполнитель'
}

# Валюты
CURRENCIES = ['USD', 'EUR', 'RUB', 'UAH', 'KZT']

# Времена
TIMEZONE = 'UTC'
DATE_FORMAT = '%d.%m.%Y %H:%M'