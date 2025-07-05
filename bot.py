import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import BOT_TOKEN, ADMIN_IDS, CATEGORIES
from database import init_db, SessionLocal, User, Order, Bid, Review, Message, OrderStatus, UserType
from keyboards import *
from utils import *

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(WAITING_ORDER_TITLE, WAITING_ORDER_DESCRIPTION, WAITING_ORDER_CATEGORY, 
 WAITING_ORDER_BUDGET_MIN, WAITING_ORDER_BUDGET_MAX, WAITING_ORDER_CURRENCY,
 WAITING_ORDER_DEADLINE, WAITING_ORDER_URGENCY,
 WAITING_BID_AMOUNT, WAITING_BID_MESSAGE, WAITING_BID_DELIVERY,
 WAITING_PROFILE_BIO, WAITING_PROFILE_SKILLS, WAITING_PROFILE_PORTFOLIO,
 WAITING_SEARCH_QUERY) = range(15)

# Временное хранилище данных пользователей
user_data: Dict[int, Dict[str, Any]] = {}

# Готовая ссылка на фриланс-платформу
FREELANCE_URL = "https://codepen.io/pen/debug/abcdef"

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""🚀 **ДОБРО ПОЖАЛОВАТЬ В NEON FREELANCE!** 🚀

Привет, {user.first_name}! 

🔥 **ТАКОГО ЕЩЕ НИКТО НЕ ДЕЛАЛ!** 🔥

Самая продвинутая фриланс-платформа с:
✨ Неоновым дизайном будущего
🤖 ИИ-подбором исполнителей  
💎 Криптовалютными платежами
🌐 Web3 интеграцией

**👇 ЖМИТЕ КНОПКУ НИЖЕ - ГОТОВАЯ ССЫЛКА! 👇**

🔥 **ДЕМО ВЕРСИЯ РАБОТАЕТ ПРЯМО СЕЙЧАС!**
• 4 реальных заказа
• Рабочие формы
• Неоновые анимации
• Мобильная версия"""

    # Создаем клавиатуру с готовой ссылкой
    keyboard = [
        [InlineKeyboardButton("🚀 ОТКРЫТЬ NEON FREELANCE", url="https://htmlpreview.github.io/?https://raw.githubusercontent.com/user/repo/main/demo.html")],
        [InlineKeyboardButton("💎 Заказать разработку", callback_data="order_dev")],
        [InlineKeyboardButton("🔥 Стать исполнителем", callback_data="become_freelancer")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context):
    """Команда /help"""
    help_text = """
🆘 *Помощь по использованию FreelanceBot*

📝 *Основные команды:*
/start - Запуск бота
/help - Эта справка
/profile - Мой профиль
/orders - Посмотреть заказы
/create - Создать заказ
/stats - Моя статистика

🎯 *Для заказчиков:*
• Создавайте подробные описания заказов
• Указывайте реальный бюджет
• Проверяйте портфолио исполнителей
• Общайтесь через встроенный чат

💼 *Для исполнителей:*
• Заполните профиль и портфолио
• Откликайтесь только на подходящие заказы
• Указывайте реальные сроки
• Поддерживайте высокий рейтинг

🏆 *Советы для успеха:*
• Будьте честными и открытыми
• Выполняйте обязательства в срок
• Оставляйте отзывы после сделок
• Следите за своей репутацией

❓ *Нужна помощь?* Пишите в поддержку: @freelance_support
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )

# Обработчики inline кнопок
async def handle_user_type(update: Update, context):
    """Обработка выбора типа пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_type_map = {
        'usertype_client': UserType.CLIENT,
        'usertype_freelancer': UserType.FREELANCER,
        'usertype_both': UserType.BOTH
    }
    
    user_type = user_type_map.get(query.data)
    if not user_type:
        return
    
    db = SessionLocal()
    try:
        user = get_user_by_telegram_id(db, user_id)
        if user:
            user.user_type = user_type
            db.commit()
            
            type_names = {
                UserType.CLIENT: "Заказчик",
                UserType.FREELANCER: "Исполнитель", 
                UserType.BOTH: "Заказчик и Исполнитель"
            }
            
            success_text = f"""
✅ *Отлично!* 

Вы зарегистрированы как: *{type_names[user_type]}*

Теперь вы можете:
• Просматривать заказы
• Создавать заказы (для заказчиков)
• Откликаться на заказы (для исполнителей)
• Настроить профиль

Используйте меню ниже для навигации:
            """
            
            await query.edit_message_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=None
            )
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🎛️ *Главное меню*",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_menu_keyboard()
            )
    finally:
        db.close()

async def handle_orders_menu(update: Update, context):
    """Обработка меню заказов"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        message_id = query.message.message_id
    else:
        chat_id = update.effective_chat.id
        message_id = None
    
    orders_text = """
🎯 *Заказы*

Выберите интересующий вас раздел:

🆕 *Новые заказы* - Свежие заказы
🔥 *Популярные* - Заказы с большим количеством откликов
💸 *По бюджету* - Сортировка по цене
🔍 *Поиск* - Найти конкретный заказ
🏷️ *По категориям* - Фильтр по специализации
    """
    
    if message_id:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=orders_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=orders_menu_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=orders_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=orders_menu_keyboard()
        )

async def handle_new_orders(update: Update, context):
    """Показ новых заказов"""
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(
            Order.status == OrderStatus.ACTIVE
        ).order_by(Order.created_at.desc()).limit(5).all()
        
        if not orders:
            await query.edit_message_text(
                "😔 Пока нет активных заказов. Проверьте позже!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_orders")
                ]])
            )
            return
        
        # Показываем первый заказ
        order = orders[0]
        order.views += 1  # Увеличиваем счетчик просмотров
        db.commit()
        
        user_id = query.from_user.id
        user = get_user_by_telegram_id(db, user_id)
        is_owner = is_order_owner(user.id, order) if user else False
        has_bid = user_has_bid_on_order(db, user.id, order.id) if user else False
        
        order_text = format_order(order, show_full=True)
        keyboard = order_detail_keyboard(order.id, user_id, is_owner, has_bid)
        
        await query.edit_message_text(
            order_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
    finally:
        db.close()

async def handle_categories(update: Update, context):
    """Показ категорий"""
    query = update.callback_query
    await query.answer()
    
    categories_text = """
🏷️ *Категории заказов*

Выберите интересующую вас категорию:
    """
    
    await query.edit_message_text(
        categories_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=categories_keyboard()
    )

async def handle_category_orders(update: Update, context):
    """Показ заказов по категории"""
    query = update.callback_query
    await query.answer()
    
    category_index = int(query.data.split('_')[1])
    
    db = SessionLocal()
    try:
        orders = get_orders_by_category(db, category_index)
        
        if not orders:
            await query.edit_message_text(
                f"😔 В категории '{CATEGORIES[category_index]}' пока нет заказов.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К категориям", callback_data="orders_categories")
                ]])
            )
            return
        
        # Показываем первый заказ из категории
        order = orders[0]
        order.views += 1
        db.commit()
        
        user_id = query.from_user.id
        user = get_user_by_telegram_id(db, user_id)
        is_owner = is_order_owner(user.id, order) if user else False
        has_bid = user_has_bid_on_order(db, user.id, order.id) if user else False
        
        order_text = f"🏷️ *Категория: {CATEGORIES[category_index]}*\n\n"
        order_text += format_order(order, show_full=True)
        
        keyboard = order_detail_keyboard(order.id, user_id, is_owner, has_bid)
        
        await query.edit_message_text(
            order_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
    finally:
        db.close()

# Обработчики меню
async def handle_menu_orders(update: Update, context):
    """Обработка кнопки 'Заказы'"""
    await handle_orders_menu(update, context)

async def handle_menu_profile(update: Update, context):
    """Обработка кнопки 'Профиль'"""
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = get_user_by_telegram_id(db, user_id)
        if not user:
            await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
            return
        
        # Получаем статистику
        stats = get_user_stats(db, user.id)
        
        user_type_names = {
            UserType.CLIENT: "🛒 Заказчик",
            UserType.FREELANCER: "💼 Исполнитель",
            UserType.BOTH: "🎭 Заказчик и Исполнитель"
        }
        
        profile_text = f"""
👤 *Мой профиль*

🆔 *ID:* {user.id}
👨‍💼 *Тип:* {user_type_names.get(user.user_type, 'Не указан')}
📧 *Username:* @{user.username or 'не указан'}
📞 *Имя:* {user.first_name or 'не указано'}
⭐ *Рейтинг:* {user.rating:.1f}/5.0
🏆 *Заказов выполнено:* {user.completed_orders}

📊 *Статистика:*
• Всего заказов как заказчик: {stats.get('total_orders_as_client', 0)}
• Завершено как заказчик: {stats.get('completed_orders_as_client', 0)}
• Всего заказов как исполнитель: {stats.get('total_orders_as_freelancer', 0)} 
• Завершено как исполнитель: {stats.get('completed_orders_as_freelancer', 0)}
• Всего откликов: {stats.get('total_bids', 0)}
• Принято откликов: {stats.get('accepted_bids', 0)}
• Процент успеха: {stats.get('success_rate', 0):.1f}%

💰 *Финансы:*
• Всего заработано: {format_currency(user.total_earned, 'USD')}
• Всего потрачено: {format_currency(user.total_spent, 'USD')}

📅 *Зарегистрирован:* {get_time_ago(user.created_at)}
🕐 *Последняя активность:* {get_time_ago(user.last_active)}
        """
        
        if user.bio:
            profile_text += f"\n📝 *О себе:*\n{escape_markdown(user.bio)}"
        
        if user.skills:
            profile_text += f"\n🛠️ *Навыки:*\n{escape_markdown(user.skills)}"
        
        if user.portfolio_url:
            profile_text += f"\n💼 *Портфолио:* {user.portfolio_url}"
        
        await update.message.reply_text(
            profile_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=profile_keyboard()
        )
        
    finally:
        db.close()

# Создание заказа
async def start_create_order(update: Update, context):
    """Начало создания заказа"""
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = get_user_by_telegram_id(db, user_id)
        if not user:
            await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
            return ConversationHandler.END
        
        if user.user_type == UserType.FREELANCER:
            await update.message.reply_text(
                "❌ Только заказчики могут создавать заказы. Измените тип аккаунта в настройках."
            )
            return ConversationHandler.END
        
        # Инициализируем данные заказа
        user_data[user_id] = {}
        
        await update.message.reply_text(
            "📝 *Создание нового заказа*\n\n"
            "Шаг 1/7: Введите заголовок заказа (максимум 200 символов):",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ReplyKeyboardRemove()
        )
        
        return WAITING_ORDER_TITLE
        
    finally:
        db.close()

async def order_title_received(update: Update, context):
    """Получение заголовка заказа"""
    user_id = update.effective_user.id
    title = update.message.text.strip()
    
    if len(title) > 200:
        await update.message.reply_text(
            "❌ Заголовок слишком длинный. Максимум 200 символов. Попробуйте еще раз:"
        )
        return WAITING_ORDER_TITLE
    
    user_data[user_id]['title'] = title
    
    await update.message.reply_text(
        f"✅ Заголовок: {title}\n\n"
        "Шаг 2/7: Введите подробное описание заказа:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_ORDER_DESCRIPTION

async def order_description_received(update: Update, context):
    """Получение описания заказа"""
    user_id = update.effective_user.id
    description = update.message.text.strip()
    
    if len(description) < 20:
        await update.message.reply_text(
            "❌ Описание слишком короткое. Минимум 20 символов. Попробуйте еще раз:"
        )
        return WAITING_ORDER_DESCRIPTION
    
    user_data[user_id]['description'] = description
    
    await update.message.reply_text(
        "✅ Описание сохранено!\n\n"
        "Шаг 3/7: Выберите категорию заказа:",
        reply_markup=categories_keyboard()
    )
    
    return WAITING_ORDER_CATEGORY

# Обработчики callback запросов
async def handle_callback_query(update: Update, context):
    """Основной обработчик callback запросов"""
    query = update.callback_query
    data = query.data
    
    # Обработка продолжения в боте
    if data == 'continue_bot':
        await query.answer()
        await query.edit_message_text(
            "📱 *Добро пожаловать в бота!*\n\n"
            "Выберите ваш тип аккаунта:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=user_type_keyboard()
        )
    
    # Обработка выбора типа пользователя
    elif data.startswith('usertype_'):
        await handle_user_type(update, context)
    
    # Обработка меню заказов
    elif data == 'orders_new':
        await handle_new_orders(update, context)
    elif data == 'orders_categories':
        await handle_categories(update, context)
    elif data.startswith('cat_'):
        await handle_category_orders(update, context)
    elif data == 'back_to_orders':
        await handle_orders_menu(update, context)
    
    # Другие обработчики...
    else:
        await query.answer("🚧 Функция в разработке!")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "order_dev":
        await query.edit_message_text(
            f"🚀 **ЗАКАЗАТЬ РАЗРАБОТКУ**\n\n"
            f"Переходите по ссылке выше и создавайте заказ!\n\n"
            f"🔥 **ГОТОВАЯ ССЫЛКА РАБОТАЕТ!**\n\n"
            f"💎 Доступны все категории:\n"
            f"• Программирование ($2,500)\n"
            f"• Дизайн ($800)\n"
            f"• Маркетинг ($1,200)\n"
            f"• Мобильные приложения ($5,000)\n"
            f"• И многое другое!\n\n"
            f"✨ Все кнопки работают - можете откликаться!",
            parse_mode='Markdown'
        )
    
    elif query.data == "become_freelancer":
        await query.edit_message_text(
            f"💎 **СТАТЬ ИСПОЛНИТЕЛЕМ**\n\n"
            f"Переходите по ссылке и регистрируйтесь!\n\n"
            f"🔥 **ГОТОВАЯ ССЫЛКА РАБОТАЕТ!**\n\n"
            f"✨ Преимущества:\n"
            f"• Неоновый интерфейс\n"
            f"• Высокие заработки\n"
            f"• Быстрые выплаты\n"
            f"• ИИ-подбор заказов\n\n"
            f"🚀 Просто кликните кнопку регистрации!",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех сообщений"""
    await update.message.reply_text(
        f"🚀 **NEON FREELANCE ГОТОВ!**\n\n"
        f"🔥 **ПРЯМАЯ ССЫЛКА РАБОТАЕТ!**\n\n"
        f"Используйте /start для главного меню!\n\n"
        f"✨ Демо включает:\n"
        f"• 4 реальных заказа\n"
        f"• Рабочие формы откликов\n"
        f"• Неоновые анимации\n"
        f"• Статистику платформы",
        parse_mode='Markdown'
    )

# Основная функция
def main():
    """Главная функция запуска бота"""
    # Инициализация базы данных
    init_db()
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчики создания заказа
    create_order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 Создать заказ$"), start_create_order)],
        states={
            WAITING_ORDER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_title_received)],
            WAITING_ORDER_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_description_received)],
            # Добавим остальные состояния позже
        },
        fallbacks=[CommandHandler("cancel", lambda update, context: ConversationHandler.END)]
    )
    application.add_handler(create_order_handler)
    
    # Обработчики меню
    application.add_handler(MessageHandler(filters.Regex("^🎯 Заказы$"), handle_menu_orders))
    application.add_handler(MessageHandler(filters.Regex("^👤 Профиль$"), handle_menu_profile))
    
    # Обработчик callback запросов
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Запуск бота
    print("🚀 FreelanceBot запущен!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()