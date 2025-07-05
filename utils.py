import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from database import User, Order, Bid, Review, Message, Notification, get_db, OrderStatus, UserType
from config import DATE_FORMAT, CATEGORIES, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

# Форматирование текста
def escape_markdown(text: str) -> str:
    """Экранирование символов для Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_currency(amount: float, currency: str) -> str:
    """Форматирование валюты"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'RUB': '₽',
        'UAH': '₴',
        'KZT': '₸'
    }
    symbol = symbols.get(currency, currency)
    return f"{amount:,.0f} {symbol}"

def format_datetime(dt: datetime) -> str:
    """Форматирование даты и времени"""
    return dt.strftime(DATE_FORMAT)

def get_time_ago(dt: datetime) -> str:
    """Получение времени 'назад'"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} дн. назад"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ч. назад"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} мин. назад"
    else:
        return "только что"

# Работа с пользователями
def get_or_create_user(db: Session, telegram_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None) -> User:
    """Получение или создание пользователя"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Обновляем информацию
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.last_active = datetime.utcnow()
        db.commit()
    
    return user

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Получение пользователя по telegram_id"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def update_user_rating(db: Session, user_id: int):
    """Обновление рейтинга пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        user.rating = total_rating / len(reviews)
    else:
        user.rating = 0.0
    
    db.commit()

# Работа с заказами
def format_order(order: Order, show_full: bool = False) -> str:
    """Форматирование заказа для отображения"""
    client_name = order.client.first_name or order.client.username or "Заказчик"
    
    text = f"📋 *{escape_markdown(order.title)}*\n\n"
    
    if show_full:
        text += f"📝 *Описание:*\n{escape_markdown(order.description)}\n\n"
    else:
        # Краткое описание (первые 100 символов)
        desc = order.description[:100] + "..." if len(order.description) > 100 else order.description
        text += f"📝 {escape_markdown(desc)}\n\n"
    
    text += f"🏷️ *Категория:* {order.category}\n"
    
    if order.budget_min and order.budget_max:
        text += f"💰 *Бюджет:* {format_currency(order.budget_min, order.currency)} - {format_currency(order.budget_max, order.currency)}\n"
    elif order.budget_min:
        text += f"💰 *Бюджет от:* {format_currency(order.budget_min, order.currency)}\n"
    elif order.budget_max:
        text += f"💰 *Бюджет до:* {format_currency(order.budget_max, order.currency)}\n"
    
    if order.deadline:
        text += f"⏰ *Срок:* {format_datetime(order.deadline)}\n"
    
    text += f"👤 *Заказчик:* {escape_markdown(client_name)}\n"
    text += f"⭐ *Рейтинг:* {order.client.rating:.1f}/5.0\n"
    text += f"📊 *Заказов:* {order.client.total_orders}\n"
    
    if order.is_urgent:
        text += f"🚀 *СРОЧНО!*\n"
    
    text += f"👁️ *Просмотров:* {order.views}\n"
    text += f"💬 *Откликов:* {len(order.bids)}\n"
    text += f"🕐 *Создан:* {get_time_ago(order.created_at)}\n"
    
    return text

def get_orders_by_category(db: Session, category_index: int, limit: int = 10) -> List[Order]:
    """Получение заказов по категории"""
    if 0 <= category_index < len(CATEGORIES):
        category = CATEGORIES[category_index]
        return db.query(Order).filter(
            Order.category == category,
            Order.status == OrderStatus.ACTIVE
        ).order_by(Order.created_at.desc()).limit(limit).all()
    return []

def search_orders(db: Session, query: str, limit: int = 10) -> List[Order]:
    """Поиск заказов"""
    return db.query(Order).filter(
        Order.status == OrderStatus.ACTIVE,
        Order.title.contains(query) | Order.description.contains(query)
    ).order_by(Order.created_at.desc()).limit(limit).all()

# Работа с откликами
def format_bid(bid: Bid) -> str:
    """Форматирование отклика"""
    freelancer_name = bid.freelancer.first_name or bid.freelancer.username or "Исполнитель"
    
    text = f"💰 *Предложение:* {format_currency(bid.amount, bid.currency)}\n"
    text += f"👤 *Исполнитель:* {escape_markdown(freelancer_name)}\n"
    text += f"⭐ *Рейтинг:* {bid.freelancer.rating:.1f}/5.0\n"
    text += f"✅ *Выполнено заказов:* {bid.freelancer.completed_orders}\n"
    
    if bid.delivery_time:
        text += f"⏱️ *Срок выполнения:* {bid.delivery_time} дн.\n"
    
    if bid.message:
        text += f"\n📝 *Комментарий:*\n{escape_markdown(bid.message)}\n"
    
    text += f"\n🕐 *Отклик отправлен:* {get_time_ago(bid.created_at)}"
    
    return text

def user_has_bid_on_order(db: Session, user_id: int, order_id: int) -> bool:
    """Проверка есть ли у пользователя отклик на заказ"""
    bid = db.query(Bid).filter(
        Bid.freelancer_id == user_id,
        Bid.order_id == order_id
    ).first()
    return bid is not None

# Работа с файлами
def is_allowed_file(filename: str) -> bool:
    """Проверка разрешенного типа файла"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_file_hash(file_content: bytes) -> str:
    """Получение хеша файла"""
    return hashlib.md5(file_content).hexdigest()

def save_file(file_content: bytes, filename: str) -> str:
    """Сохранение файла"""
    os.makedirs("uploads", exist_ok=True)
    file_hash = get_file_hash(file_content)
    ext = os.path.splitext(filename)[1]
    new_filename = f"{file_hash}{ext}"
    filepath = os.path.join("uploads", new_filename)
    
    if not os.path.exists(filepath):
        with open(filepath, 'wb') as f:
            f.write(file_content)
    
    return filepath

# Работа с уведомлениями
def create_notification(db: Session, user_id: int, title: str, message: str, 
                       notification_type: str = None):
    """Создание уведомления"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    db.add(notification)
    db.commit()

def get_unread_notifications_count(db: Session, user_id: int) -> int:
    """Получение количества непрочитанных уведомлений"""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()

# Проверки доступа
def is_order_owner(user_id: int, order: Order) -> bool:
    """Проверка является ли пользователь владельцем заказа"""
    return order.client_id == user_id

def can_bid_on_order(user: User, order: Order) -> bool:
    """Проверка может ли пользователь откликнуться на заказ"""
    if user.id == order.client_id:
        return False
    if user.user_type == UserType.CLIENT:
        return False
    if order.status != OrderStatus.ACTIVE:
        return False
    return True

# Статистика
def get_user_stats(db: Session, user_id: int) -> dict:
    """Получение статистики пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}
    
    # Заказы как заказчик
    client_orders = db.query(Order).filter(Order.client_id == user_id).count()
    completed_as_client = db.query(Order).filter(
        Order.client_id == user_id,
        Order.status == OrderStatus.COMPLETED
    ).count()
    
    # Заказы как исполнитель
    freelancer_orders = db.query(Order).filter(Order.freelancer_id == user_id).count()
    completed_as_freelancer = db.query(Order).filter(
        Order.freelancer_id == user_id,
        Order.status == OrderStatus.COMPLETED
    ).count()
    
    # Отклики
    total_bids = db.query(Bid).filter(Bid.freelancer_id == user_id).count()
    accepted_bids = db.query(Bid).filter(
        Bid.freelancer_id == user_id,
        Bid.is_accepted == True
    ).count()
    
    return {
        'total_orders_as_client': client_orders,
        'completed_orders_as_client': completed_as_client,
        'total_orders_as_freelancer': freelancer_orders,
        'completed_orders_as_freelancer': completed_as_freelancer,
        'total_bids': total_bids,
        'accepted_bids': accepted_bids,
        'success_rate': (accepted_bids / total_bids * 100) if total_bids > 0 else 0,
        'rating': user.rating,
        'total_earned': user.total_earned,
        'total_spent': user.total_spent
    }

# Валидация
def validate_budget(budget_str: str) -> tuple[bool, float]:
    """Валидация бюджета"""
    try:
        budget = float(budget_str.replace(',', '.'))
        if budget <= 0:
            return False, 0
        return True, budget
    except ValueError:
        return False, 0

def validate_deadline(date_str: str) -> tuple[bool, datetime]:
    """Валидация срока"""
    try:
        deadline = datetime.strptime(date_str, '%d.%m.%Y')
        if deadline < datetime.now():
            return False, None
        return True, deadline
    except ValueError:
        return False, None

# Пагинация
def paginate_items(items: list, page: int, per_page: int = 5) -> tuple[list, int, int]:
    """Пагинация элементов"""
    total_pages = (len(items) - 1) // per_page + 1 if items else 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return items[start_idx:end_idx], page, total_pages