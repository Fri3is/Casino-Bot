from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from config import CATEGORIES, CURRENCIES

# Главное меню
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("🎯 Заказы"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("💼 Мои заказы"), KeyboardButton("📝 Создать заказ")],
        [KeyboardButton("💬 Сообщения"), KeyboardButton("📊 Статистика")],
        [KeyboardButton("⚙️ Настройки"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Inline меню для заказов
def orders_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🆕 Новые заказы", callback_data="orders_new")],
        [InlineKeyboardButton("🔥 Популярные", callback_data="orders_popular")],
        [InlineKeyboardButton("💸 По бюджету", callback_data="orders_budget")],
        [InlineKeyboardButton("🔍 Поиск", callback_data="orders_search")],
        [InlineKeyboardButton("🏷️ По категориям", callback_data="orders_categories")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура категорий
def categories_keyboard():
    keyboard = []
    for i in range(0, len(CATEGORIES), 2):
        row = [InlineKeyboardButton(CATEGORIES[i], callback_data=f"cat_{i}")]
        if i + 1 < len(CATEGORIES):
            row.append(InlineKeyboardButton(CATEGORIES[i + 1], callback_data=f"cat_{i+1}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_orders")])
    return InlineKeyboardMarkup(keyboard)

# Клавиатура валют
def currencies_keyboard():
    keyboard = []
    for i in range(0, len(CURRENCIES), 3):
        row = []
        for j in range(3):
            if i + j < len(CURRENCIES):
                row.append(InlineKeyboardButton(CURRENCIES[i + j], callback_data=f"curr_{CURRENCIES[i + j]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для конкретного заказа
def order_detail_keyboard(order_id, user_id, is_owner=False, has_bid=False):
    keyboard = []
    
    if is_owner:
        keyboard.extend([
            [InlineKeyboardButton("📝 Редактировать", callback_data=f"edit_order_{order_id}")],
            [InlineKeyboardButton("👥 Отклики", callback_data=f"order_bids_{order_id}")],
            [InlineKeyboardButton("❌ Удалить", callback_data=f"delete_order_{order_id}")]
        ])
    else:
        if not has_bid:
            keyboard.append([InlineKeyboardButton("💰 Откликнуться", callback_data=f"bid_order_{order_id}")])
        else:
            keyboard.append([InlineKeyboardButton("✏️ Изменить отклик", callback_data=f"edit_bid_{order_id}")])
    
    keyboard.extend([
        [InlineKeyboardButton("💬 Написать автору", callback_data=f"message_author_{order_id}")],
        [InlineKeyboardButton("📤 Поделиться", callback_data=f"share_order_{order_id}")],
        [InlineKeyboardButton("🔙 К заказам", callback_data="orders_new")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

# Клавиатура профиля
def profile_keyboard():
    keyboard = [
        [InlineKeyboardButton("📝 Редактировать профиль", callback_data="edit_profile")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="my_reviews")],
        [InlineKeyboardButton("💼 Портфолио", callback_data="my_portfolio")],
        [InlineKeyboardButton("📊 Статистика", callback_data="my_stats")],
        [InlineKeyboardButton("🔔 Уведомления", callback_data="notifications")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура выбора типа пользователя
def user_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 Заказчик", callback_data="usertype_client")],
        [InlineKeyboardButton("💼 Исполнитель", callback_data="usertype_freelancer")],
        [InlineKeyboardButton("🎭 Заказчик и Исполнитель", callback_data="usertype_both")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура рейтинга
def rating_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⭐ 1", callback_data="rating_1"),
            InlineKeyboardButton("⭐⭐ 2", callback_data="rating_2"),
            InlineKeyboardButton("⭐⭐⭐ 3", callback_data="rating_3")
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data="rating_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data="rating_5")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для откликов
def bids_keyboard(order_id, bids):
    keyboard = []
    for bid in bids[:10]:  # Показываем максимум 10 откликов
        freelancer_name = bid.freelancer.first_name or bid.freelancer.username or "Пользователь"
        keyboard.append([InlineKeyboardButton(
            f"💰 {bid.amount} {bid.currency} | {freelancer_name}",
            callback_data=f"view_bid_{bid.id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 К заказу", callback_data=f"view_order_{order_id}")])
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для работы с откликом
def bid_actions_keyboard(bid_id, order_id, is_client=False):
    keyboard = []
    
    if is_client:
        keyboard.extend([
            [InlineKeyboardButton("✅ Принять", callback_data=f"accept_bid_{bid_id}")],
            [InlineKeyboardButton("💬 Написать", callback_data=f"message_freelancer_{bid_id}")],
            [InlineKeyboardButton("👤 Профиль", callback_data=f"view_profile_{bid_id}")]
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 К откликам", callback_data=f"order_bids_{order_id}")])
    return InlineKeyboardMarkup(keyboard)

# Клавиатура настроек
def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌍 Язык", callback_data="settings_language")],
        [InlineKeyboardButton("🕐 Часовой пояс", callback_data="settings_timezone")],
        [InlineKeyboardButton("🔔 Уведомления", callback_data="settings_notifications")],
        [InlineKeyboardButton("🔒 Приватность", callback_data="settings_privacy")],
        [InlineKeyboardButton("📞 Контакты", callback_data="settings_contacts")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура подтверждения
def confirm_keyboard(action, item_id=None):
    callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
    callback_no = f"cancel_{action}_{item_id}" if item_id else f"cancel_{action}"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=callback_yes),
            InlineKeyboardButton("❌ Нет", callback_data=callback_no)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура пагинации
def pagination_keyboard(current_page, total_pages, callback_prefix):
    keyboard = []
    
    if total_pages > 1:
        row = []
        if current_page > 1:
            row.append(InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_{current_page-1}"))
        
        row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            row.append(InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_{current_page+1}"))
        
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

# Клавиатура администратора
def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("📝 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для срочности заказа
def urgency_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Срочно (+50% к стоимости)", callback_data="urgent_yes")],
        [InlineKeyboardButton("📅 Обычно", callback_data="urgent_no")]
    ]
    return InlineKeyboardMarkup(keyboard)