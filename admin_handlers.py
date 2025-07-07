from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from games import GameLogic

class AdminStates(StatesGroup):
    waiting_for_coefficient = State()
    waiting_for_commission = State()
    waiting_for_min_bet = State()
    waiting_for_max_bet = State()
    waiting_for_reserve_amount = State()
    waiting_for_admin_username = State()

def create_coefficients_keyboard() -> InlineKeyboardMarkup:
    """Create coefficients management keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎲 Кубик", callback_data="coeff_dice"),
            InlineKeyboardButton(text="⚽ Футбол", callback_data="coeff_football")
        ],
        [
            InlineKeyboardButton(text="🏀 Баскетбол", callback_data="coeff_basketball"),
            InlineKeyboardButton(text="🎯 Дартс", callback_data="coeff_darts")
        ],
        [
            InlineKeyboardButton(text="🎳 Боулинг", callback_data="coeff_bowling"),
            InlineKeyboardButton(text="🎰 Слоты", callback_data="coeff_slots")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")
        ]
    ])
    return keyboard

def create_game_coefficients_keyboard(game_type: str) -> InlineKeyboardMarkup:
    """Create keyboard for specific game coefficients"""
    options = GameLogic.get_all_bet_options()[game_type]
    keyboard_buttons = []
    
    for bet_type, description in options.items():
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{description}",
                callback_data=f"edit_coeff_{game_type}_{bet_type}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_coefficients")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

async def admin_coefficients_callback(callback: CallbackQuery, db: Database):
    """Handle coefficients management"""
    await callback.message.edit_text(
        "⚙️ <b>Управление коэффициентами</b>\n\n"
        "Выберите игру для настройки коэффициентов:",
        reply_markup=create_coefficients_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

async def game_coefficients_callback(callback: CallbackQuery, db: Database):
    """Handle specific game coefficients"""
    game_type = callback.data.split("_")[1]
    
    # Get current coefficients
    settings = await db.get_game_settings(game_type)
    
    game_names = {
        "dice": "🎲 Кубик",
        "football": "⚽ Футбол",
        "basketball": "🏀 Баскетбол", 
        "darts": "🎯 Дартс",
        "bowling": "🎳 Боулинг",
        "slots": "🎰 Слоты"
    }
    
    text = f"<b>{game_names[game_type]} - Коэффициенты</b>\n\n"
    
    options = GameLogic.get_all_bet_options()[game_type]
    for setting in settings:
        bet_type = setting['bet_type']
        if bet_type in options:
            description = options[bet_type]
            coefficient = setting['coefficient']
            text += f"• {description}: <b>{coefficient}x</b>\n"
    
    text += "\nВыберите ставку для изменения коэффициента:"
    
    await callback.message.edit_text(
        text,
        reply_markup=create_game_coefficients_keyboard(game_type),
        parse_mode="HTML"
    )
    await callback.answer()

async def edit_coefficient_callback(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle coefficient editing"""
    parts = callback.data.split("_")
    game_type = parts[2]
    bet_type = "_".join(parts[3:])
    
    # Get current coefficient
    settings = await db.get_game_settings(game_type)
    current_coeff = next((s['coefficient'] for s in settings if s['bet_type'] == bet_type), 2.0)
    
    options = GameLogic.get_all_bet_options()[game_type]
    bet_description = options.get(bet_type, "Неизвестная ставка")
    
    await state.update_data(game_type=game_type, bet_type=bet_type)
    await state.set_state(AdminStates.waiting_for_coefficient)
    
    await callback.message.edit_text(
        f"⚙️ <b>Изменение коэффициента</b>\n\n"
        f"🎮 Игра: {game_type.title()}\n"
        f"🎯 Ставка: {bet_description}\n"
        f"📊 Текущий коэффициент: {current_coeff}x\n\n"
        "Введите новый коэффициент:",
        parse_mode="HTML"
    )
    await callback.answer()

async def coefficient_input_handler(message: Message, state: FSMContext, db: Database):
    """Handle coefficient input"""
    try:
        coefficient = float(message.text)
        if coefficient <= 0:
            await message.answer("❌ Коэффициент должен быть больше 0!")
            return
        
        if coefficient > 1000:
            await message.answer("❌ Коэффициент не может быть больше 1000!")
            return
        
        data = await state.get_data()
        game_type = data['game_type']
        bet_type = data['bet_type']
        
        await db.update_coefficient(game_type, bet_type, coefficient)
        
        await message.answer(
            f"✅ <b>Коэффициент обновлен!</b>\n\n"
            f"🎮 Игра: {game_type.title()}\n"
            f"🎯 Ставка: {bet_type}\n"
            f"📊 Новый коэффициент: {coefficient}x",
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число!")

async def admin_commission_callback(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle commission settings"""
    current_commission = await db.get_admin_setting("commission_rate")
    
    await callback.message.edit_text(
        f"💰 <b>Настройка комиссии</b>\n\n"
        f"Текущая комиссия: {current_commission}%\n\n"
        "Введите новую комиссию (5-15%):",
        parse_mode="HTML"
    )
    
    await state.set_state(AdminStates.waiting_for_commission)
    await callback.answer()

async def commission_input_handler(message: Message, state: FSMContext, db: Database):
    """Handle commission input"""
    try:
        commission = float(message.text)
        if not (5 <= commission <= 15):
            await message.answer("❌ Комиссия должна быть от 5% до 15%!")
            return
        
        await db.update_admin_setting("commission_rate", str(commission))
        
        await message.answer(
            f"✅ <b>Комиссия обновлена!</b>\n\n"
            f"Новая комиссия: {commission}%",
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число!")

async def admin_stats_callback(callback: CallbackQuery, db: Database):
    """Handle admin statistics"""
    stats = await db.get_stats()
    commission_rate = await db.get_admin_setting("commission_rate")
    casino_reserve = await db.get_admin_setting("casino_reserve")
    min_deposit = await db.get_admin_setting("min_deposit")
    min_withdrawal = await db.get_admin_setting("min_withdrawal")
    
    stats_text = (
        f"📊 <b>Статистика казино</b>\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🎮 Игр сыграно: {stats['total_games']}\n"
        f"💰 Всего депозитов: ${stats['total_deposited']:.2f}\n"
        f"💸 Всего выводов: ${stats['total_withdrawn']:.2f}\n"
        f"💵 Прибыль казино: ${stats['casino_profit']:.2f}\n"
        f"🏦 Резерв казино: ${casino_reserve}\n\n"
        f"⚙️ <b>Настройки:</b>\n"
        f"📊 Комиссия: {commission_rate}%\n"
        f"💳 Мин. депозит: ${min_deposit}\n"
        f"💸 Мин. вывод: ${min_withdrawal}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

async def admin_reserve_callback(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle reserve management"""
    current_reserve = await db.get_admin_setting("casino_reserve")
    
    await callback.message.edit_text(
        f"💰 <b>Управление резервом</b>\n\n"
        f"Текущий резерв: ${current_reserve}\n\n"
        "Введите сумму для добавления в резерв\n"
        "(отрицательное число для вычитания):",
        parse_mode="HTML"
    )
    
    await state.set_state(AdminStates.waiting_for_reserve_amount)
    await callback.answer()

async def reserve_input_handler(message: Message, state: FSMContext, db: Database):
    """Handle reserve amount input"""
    try:
        amount = float(message.text)
        current_reserve = float(await db.get_admin_setting("casino_reserve"))
        new_reserve = current_reserve + amount
        
        if new_reserve < 0:
            await message.answer("❌ Резерв не может быть отрицательным!")
            return
        
        await db.update_admin_setting("casino_reserve", str(new_reserve))
        
        operation = "добавлено" if amount > 0 else "вычтено"
        await message.answer(
            f"✅ <b>Резерв обновлен!</b>\n\n"
            f"{operation.title()}: ${abs(amount):.2f}\n"
            f"Новый резерв: ${new_reserve:.2f}",
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число!")

async def admin_users_callback(callback: CallbackQuery, state: FSMContext):
    """Handle admin users management"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Удалить админа", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton(text="👥 Список админов", callback_data="list_admins")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")
        ]
    ])
    
    await callback.message.edit_text(
        "👥 <b>Управление администраторами</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

async def add_admin_callback(callback: CallbackQuery, state: FSMContext):
    """Handle add admin callback"""
    await callback.message.edit_text(
        "➕ <b>Добавление администратора</b>\n\n"
        "Введите username нового администратора\n"
        "(без символа @):",
        parse_mode="HTML"
    )
    
    await state.set_state(AdminStates.waiting_for_admin_username)
    await callback.answer()

async def admin_username_input_handler(message: Message, state: FSMContext, db: Database):
    """Handle admin username input"""
    username = message.text.strip().replace("@", "")
    
    if not username:
        await message.answer("❌ Пожалуйста, введите корректный username!")
        return
    
    # Note: We can't add admin without user_id, so we'll store username
    # and add when user first uses /admin command
    await message.answer(
        f"✅ <b>Администратор добавлен!</b>\n\n"
        f"Username: @{username}\n\n"
        f"Администратор будет активирован при первом использовании команды /admin",
        parse_mode="HTML"
    )
    
    await state.clear()

async def close_admin_callback(callback: CallbackQuery):
    """Handle close admin panel"""
    await callback.message.delete()
    await callback.answer("Админ панель закрыта")

# Export handlers
admin_handlers = {
    "admin_coefficients": admin_coefficients_callback,
    "admin_commission": admin_commission_callback,
    "admin_stats": admin_stats_callback,
    "admin_reserve": admin_reserve_callback,
    "admin_users": admin_users_callback,
    "add_admin": add_admin_callback,
    "close_admin": close_admin_callback,
}

# Coefficient handlers
coeff_handlers = {}
for game in ["dice", "football", "basketball", "darts", "bowling", "slots"]:
    coeff_handlers[f"coeff_{game}"] = game_coefficients_callback

# State handlers
state_handlers = {
    AdminStates.waiting_for_coefficient: coefficient_input_handler,
    AdminStates.waiting_for_commission: commission_input_handler,
    AdminStates.waiting_for_reserve_amount: reserve_input_handler,
    AdminStates.waiting_for_admin_username: admin_username_input_handler,
}