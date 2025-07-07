import asyncio
import os
import logging
from typing import Dict, Optional, Any

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand, BotCommandScopeDefault, Dice
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from database import Database
from cryptopay import CryptoPayAPI
from games import GameLogic
from admin_handlers import (
    admin_handlers, coeff_handlers, state_handlers as admin_state_handlers,
    AdminStates, edit_coefficient_callback
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTOPAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN")
ADMIN_USERNAMES = os.getenv("ADMIN_USERNAMES", "").split(",")
DATABASE_PATH = os.getenv("DATABASE_PATH", "casino_bot.db")

# Initialize components
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database(DATABASE_PATH)
cryptopay = CryptoPayAPI(CRYPTOPAY_TOKEN)

# FSM States
class BetStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_game_result = State()

# Admin states are now imported from admin_handlers

class DepositStates(StatesGroup):
    waiting_for_amount = State()

class WithdrawStates(StatesGroup):
    waiting_for_amount = State()

# Global variables for current bets
user_bets: Dict[int, Dict[str, Any]] = {}

def create_main_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎮 Играть", callback_data="games_menu"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        [
            InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit"),
            InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help")
        ]
    ])
    return keyboard

def create_games_keyboard() -> InlineKeyboardMarkup:
    """Create games menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎲 Кубик", callback_data="game_dice"),
            InlineKeyboardButton(text="⚽ Футбол", callback_data="game_football")
        ],
        [
            InlineKeyboardButton(text="🏀 Баскетбол", callback_data="game_basketball"),
            InlineKeyboardButton(text="🎯 Дартс", callback_data="game_darts")
        ],
        [
            InlineKeyboardButton(text="🎳 Боулинг", callback_data="game_bowling"),
            InlineKeyboardButton(text="🎰 Слоты", callback_data="game_slots")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
        ]
    ])
    return keyboard

def create_bet_options_keyboard(game_type: str) -> InlineKeyboardMarkup:
    """Create betting options keyboard for specific game"""
    options = GameLogic.get_all_bet_options()[game_type]
    keyboard_buttons = []
    
    # Create rows of 2 buttons each
    buttons_row = []
    for bet_type, description in options.items():
        buttons_row.append(InlineKeyboardButton(
            text=description, 
            callback_data=f"bet_{game_type}_{bet_type}"
        ))
        
        if len(buttons_row) == 2:
            keyboard_buttons.append(buttons_row)
            buttons_row = []
    
    # Add remaining button if any
    if buttons_row:
        keyboard_buttons.append(buttons_row)
    
    # Add back button
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="games_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def create_admin_keyboard() -> InlineKeyboardMarkup:
    """Create admin panel keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️ Коэффициенты", callback_data="admin_coefficients"),
            InlineKeyboardButton(text="💰 Комиссия", callback_data="admin_commission")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Админы", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="💰 Резерв", callback_data="admin_reserve"),
            InlineKeyboardButton(text="⬅️ Закрыть", callback_data="close_admin")
        ]
    ])
    return keyboard

async def is_admin_user(user_id: int, username: str = None) -> bool:
    """Check if user is admin"""
    # Check database
    if await db.is_admin(user_id):
        return True
    
    # Check environment variable
    if username and username in ADMIN_USERNAMES:
        # Add to database
        await db.add_admin(user_id, username, user_id)
        return True
    
    return False

@dp.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Create user if not exists
    await db.create_user(user_id, username, first_name)
    
    welcome_text = (
        "🎰 <b>Добро пожаловать в Casino Bot!</b>\n\n"
        "🎮 Играйте в игры Telegram и выигрывайте!\n"
        "💰 Пополняйте баланс через CryptoPay\n"
        "🏆 Получайте выплаты за победы\n\n"
        "Выберите действие:"
    )
    
    await message.answer(welcome_text, reply_markup=create_main_keyboard(), parse_mode="HTML")

@dp.message(Command("admin"))
async def admin_command(message: Message):
    """Handle /admin command"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    if not await is_admin_user(user_id, username):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    stats = await db.get_stats()
    commission_rate = await db.get_admin_setting("commission_rate")
    casino_reserve = await db.get_admin_setting("casino_reserve")
    
    admin_text = (
        "👑 <b>Панель администратора</b>\n\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"🎮 Игр сыграно: {stats['total_games']}\n"
        f"💰 Депозитов: ${stats['total_deposited']:.2f}\n"
        f"💸 Выводов: ${stats['total_withdrawn']:.2f}\n"
        f"💵 Прибыль казино: ${stats['casino_profit']:.2f}\n"
        f"📊 Комиссия: {commission_rate}%\n"
        f"🏦 Резерв: ${casino_reserve}"
    )
    
    await message.answer(admin_text, reply_markup=create_admin_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    """Handle main menu callback"""
    await callback.message.edit_text(
        "🎰 <b>Casino Bot - Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=create_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "games_menu")
async def games_menu_callback(callback: CallbackQuery):
    """Handle games menu callback"""
    await callback.message.edit_text(
        "🎮 <b>Выберите игру:</b>\n\n"
        "🎲 <b>Кубик</b> - ставки на число, четность, суммы\n"
        "⚽ <b>Футбол</b> - гол, промах, точный удар\n"
        "🏀 <b>Баскетбол</b> - попадание, отскок, чистый бросок\n"
        "🎯 <b>Дартс</b> - сектора, центр, отскок\n"
        "🎳 <b>Боулинг</b> - страйк, количество кеглей\n"
        "🎰 <b>Слоты</b> - джекпоты, точное значение",
        reply_markup=create_games_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("game_"))
async def game_selection_callback(callback: CallbackQuery):
    """Handle game selection"""
    game_type = callback.data.split("_")[1]
    
    game_names = {
        "dice": "🎲 Кубик",
        "football": "⚽ Футбол", 
        "basketball": "🏀 Баскетбол",
        "darts": "🎯 Дартс",
        "bowling": "🎳 Боулинг",
        "slots": "🎰 Слоты"
    }
    
    await callback.message.edit_text(
        f"<b>{game_names[game_type]}</b>\n\n"
        "Выберите тип ставки:",
        reply_markup=create_bet_options_keyboard(game_type),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("bet_"))
async def bet_selection_callback(callback: CallbackQuery, state: FSMContext):
    """Handle bet type selection"""
    parts = callback.data.split("_")
    game_type = parts[1]
    bet_type = "_".join(parts[2:])
    
    # Get coefficient from database
    settings = await db.get_game_settings(game_type)
    coefficient = next((s['coefficient'] for s in settings if s['bet_type'] == bet_type), 2.0)
    
    # Store bet info
    user_bets[callback.from_user.id] = {
        'game_type': game_type,
        'bet_type': bet_type,
        'coefficient': coefficient
    }
    
    bet_description = GameLogic.get_all_bet_options()[game_type][bet_type]
    
    await callback.message.edit_text(
        f"<b>Ставка выбрана:</b>\n"
        f"🎮 Игра: {GameLogic.get_game_emoji(game_type)} {game_type.title()}\n"
        f"🎯 Ставка: {bet_description}\n"
        f"📊 Коэффициент: {coefficient}x\n\n"
        "💰 Введите сумму ставки:",
        parse_mode="HTML"
    )
    
    await state.set_state(BetStates.waiting_for_amount)
    await callback.answer()

@dp.message(BetStates.waiting_for_amount)
async def bet_amount_handler(message: Message, state: FSMContext):
    """Handle bet amount input"""
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0!")
            return
        
        user_id = message.from_user.id
        balance = await db.get_user_balance(user_id)
        
        if amount > balance:
            await message.answer(f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}")
            return
        
        # Store amount and proceed to game
        if user_id not in user_bets:
            await message.answer("❌ Ошибка: информация о ставке потеряна. Начните заново.")
            await state.clear()
            return
        
        user_bets[user_id]['amount'] = amount
        
        # Deduct bet amount from balance
        await db.update_user_balance(user_id, -amount)
        
        bet_info = user_bets[user_id]
        game_emoji = GameLogic.get_game_emoji(bet_info['game_type'])
        
        await message.answer(
            f"✅ <b>Ставка принята!</b>\n\n"
            f"🎮 Игра: {game_emoji}\n"
            f"💰 Сумма: ${amount:.2f}\n"
            f"📊 Коэффициент: {bet_info['coefficient']}x\n"
            f"💵 Возможный выигрыш: ${amount * bet_info['coefficient']:.2f}\n\n"
            f"Отправьте {game_emoji} чтобы начать игру!",
            parse_mode="HTML"
        )
        
        await state.set_state(BetStates.waiting_for_game_result)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму!")

@dp.message(BetStates.waiting_for_game_result, F.dice)
async def game_result_handler(message: Message, state: FSMContext):
    """Handle game result from dice"""
    user_id = message.from_user.id
    
    if user_id not in user_bets:
        await message.answer("❌ Ставка не найдена!")
        await state.clear()
        return
    
    bet_info = user_bets[user_id]
    dice_value = message.dice.value
    
    # Check if the game type matches the dice
    expected_emoji = GameLogic.get_game_emoji(bet_info['game_type'])
    if message.dice.emoji != expected_emoji:
        await message.answer(f"❌ Неправильная игра! Ожидается: {expected_emoji}")
        return
    
    # Check bet result
    won = GameLogic.check_bet_result(
        bet_info['game_type'], 
        dice_value, 
        bet_info['bet_type']
    )
    
    # Handle special "better" game types
    coefficient = bet_info['coefficient']
    if bet_info['bet_type'] == "better":
        coefficient = GameLogic.get_better_coefficient(
            bet_info['game_type'], 
            dice_value, 
            coefficient
        )
        won = True  # Always win in "better" games
    
    # Calculate winnings
    bet_amount = bet_info['amount']
    win_amount = 0
    commission = 0
    
    if won:
        win_amount = bet_amount * coefficient
        commission_rate = float(await db.get_admin_setting("commission_rate")) / 100
        commission = win_amount * commission_rate
        final_win_amount = win_amount - commission
        
        # Add winnings to balance
        await db.update_user_balance(user_id, final_win_amount)
        
        # Update casino reserve
        current_reserve = float(await db.get_admin_setting("casino_reserve"))
        await db.update_admin_setting("casino_reserve", str(current_reserve + commission))
    
    # Record game in history
    await db.add_game_record(
        user_id, bet_info['game_type'], bet_info['bet_type'],
        bet_amount, dice_value, won, win_amount, commission
    )
    
    # Send result message
    if won:
        result_text = (
            f"🎉 <b>Поздравляем! Вы выиграли!</b>\n\n"
            f"🎮 Результат: {dice_value}\n"
            f"💰 Ставка: ${bet_amount:.2f}\n"
            f"📊 Коэффициент: {coefficient}x\n"
            f"💵 Выигрыш: ${win_amount:.2f}\n"
            f"🏦 Комиссия: ${commission:.2f}\n"
            f"✅ К выплате: ${win_amount - commission:.2f}"
        )
    else:
        result_text = (
            f"😞 <b>К сожалению, вы проиграли!</b>\n\n"
            f"🎮 Результат: {dice_value}\n"
            f"💰 Ставка: ${bet_amount:.2f}\n"
            f"📊 Попробуйте еще раз!"
        )
    
    await message.answer(result_text, parse_mode="HTML")
    await message.answer("Хотите сыграть еще?", reply_markup=create_main_keyboard())
    
    # Clear bet info and state
    del user_bets[user_id]
    await state.clear()

@dp.callback_query(F.data == "balance")
async def balance_callback(callback: CallbackQuery):
    """Handle balance callback"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден!")
        return
    
    balance_text = (
        f"💰 <b>Ваш баланс</b>\n\n"
        f"💵 Текущий баланс: ${user['balance']:.2f}\n"
        f"📈 Всего пополнено: ${user['total_deposited']:.2f}\n"
        f"📉 Всего выведено: ${user['total_withdrawn']:.2f}\n"
        f"🏆 Всего выиграно: ${user['total_won']:.2f}\n"
        f"📊 Всего проиграно: ${user['total_lost']:.2f}\n"
        f"🎮 Игр сыграно: {user['games_played']}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit"),
            InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
        ]
    ])
    
    await callback.message.edit_text(balance_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "deposit")
async def deposit_callback(callback: CallbackQuery, state: FSMContext):
    """Handle deposit callback"""
    await callback.message.edit_text(
        "💳 <b>Пополнение баланса</b>\n\n"
        "💰 Введите сумму для пополнения (в USDT):\n"
        "Минимальная сумма: $1",
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await callback.answer()

@dp.message(DepositStates.waiting_for_amount)
async def deposit_amount_handler(message: Message, state: FSMContext):
    """Handle deposit amount input"""
    try:
        amount = float(message.text)
        min_deposit = float(await db.get_admin_setting("min_deposit"))
        
        if amount < min_deposit:
            await message.answer(f"❌ Минимальная сумма пополнения: ${min_deposit}")
            return
        
        # Create CryptoPay invoice
        invoice = await cryptopay.create_invoice(
            amount=amount,
            currency="USDT",
            description="Пополнение баланса в Casino Bot",
            user_id=message.from_user.id
        )
        
        if not invoice:
            await message.answer("❌ Ошибка создания платежа. Попробуйте позже.")
            await state.clear()
            return
        
        # Save transaction to database
        await db.add_transaction(
            message.from_user.id,
            "deposit",
            amount,
            str(invoice.get('invoice_id', '')),
            "pending"
        )
        
        # Create payment keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=invoice['pay_url'])],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
        ])
        
        await message.answer(
            f"💳 <b>Счет на пополнение создан!</b>\n\n"
            f"💰 Сумма: ${amount:.2f} USDT\n"
            f"🔢 ID счета: {invoice.get('invoice_id', 'N/A')}\n\n"
            "Нажмите кнопку ниже для оплаты:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму!")

@dp.callback_query(F.data == "withdraw")
async def withdraw_callback(callback: CallbackQuery, state: FSMContext):
    """Handle withdraw callback"""
    user_id = callback.from_user.id
    balance = await db.get_user_balance(user_id)
    min_withdrawal = await db.get_admin_setting("min_withdrawal")
    
    await callback.message.edit_text(
        f"💸 <b>Вывод средств</b>\n\n"
        f"💰 Ваш баланс: ${balance:.2f}\n"
        f"Минимальная сумма вывода: ${min_withdrawal}\n\n"
        "Введите сумму для вывода:",
        parse_mode="HTML"
    )
    await state.set_state(WithdrawStates.waiting_for_amount)
    await callback.answer()

@dp.message(WithdrawStates.waiting_for_amount)
async def withdraw_amount_handler(message: Message, state: FSMContext):
    """Handle withdraw amount input"""
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        balance = await db.get_user_balance(user_id)
        min_withdrawal = float(await db.get_admin_setting("min_withdrawal"))
        
        if amount < min_withdrawal:
            await message.answer(f"❌ Минимальная сумма вывода: ${min_withdrawal}")
            return
        
        if amount > balance:
            await message.answer(f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}")
            return
        
        # Deduct amount from balance
        await db.update_user_balance(user_id, -amount)
        
        # Try to transfer via CryptoPay
        transfer_result = await cryptopay.transfer(
            user_id=user_id,
            amount=amount,
            currency="USDT",
            comment="Вывод средств из Casino Bot"
        )
        
        if transfer_result:
            # Save successful transaction
            await db.add_transaction(user_id, "withdrawal", amount, None, "completed")
            
            await message.answer(
                f"✅ <b>Вывод успешно выполнен!</b>\n\n"
                f"💰 Сумма: ${amount:.2f} USDT\n"
                f"🔢 ID транзакции: {transfer_result.get('transfer_id', 'N/A')}\n\n"
                "Средства будут зачислены в течение нескольких минут.",
                parse_mode="HTML"
            )
        else:
            # Return money back on failure
            await db.update_user_balance(user_id, amount)
            await db.add_transaction(user_id, "withdrawal", amount, None, "failed")
            
            await message.answer(
                "❌ <b>Ошибка при выводе средств!</b>\n\n"
                "Попробуйте позже или обратитесь в поддержку.\n"
                "Средства возвращены на ваш баланс.",
                parse_mode="HTML"
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму!")

@dp.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    """Handle user statistics callback"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ Данные пользователя не найдены!")
        return
    
    win_rate = 0
    if user['games_played'] > 0:
        win_rate = (user['total_won'] / (user['total_won'] + user['total_lost'])) * 100 if (user['total_won'] + user['total_lost']) > 0 else 0
    
    profit = user['total_won'] - user['total_lost']
    profit_emoji = "📈" if profit >= 0 else "📉"
    
    stats_text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"🎮 Игр сыграно: {user['games_played']}\n"
        f"🏆 Всего выиграно: ${user['total_won']:.2f}\n"
        f"💸 Всего проиграно: ${user['total_lost']:.2f}\n"
        f"{profit_emoji} Прибыль/Убыток: ${profit:.2f}\n"
        f"📊 Винрейт: {win_rate:.1f}%\n\n"
        f"💰 <b>Финансы:</b>\n"
        f"📈 Всего пополнено: ${user['total_deposited']:.2f}\n"
        f"📉 Всего выведено: ${user['total_withdrawn']:.2f}\n"
        f"💵 Текущий баланс: ${user['balance']:.2f}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    """Handle help callback"""
    help_text = (
        "❓ <b>Помощь по Casino Bot</b>\n\n"
        "🎮 <b>Как играть:</b>\n"
        "1. Пополните баланс через CryptoPay\n"
        "2. Выберите игру и тип ставки\n"
        "3. Укажите сумму ставки\n"
        "4. Отправьте соответствующий эмодзи\n"
        "5. Получите результат и выигрыш!\n\n"
        "🎲 <b>Доступные игры:</b>\n"
        "• Кубик - ставки на числа, четность\n"
        "• Футбол - гол, промах, точность\n"
        "• Баскетбол - попадание, отскок\n"
        "• Дартс - сектора, центр мишени\n"
        "• Боулинг - страйк, количество кеглей\n"
        "• Слоты - джекпоты, комбинации\n\n"
        "💰 <b>Финансы:</b>\n"
        "• Депозиты через CryptoPay (USDT)\n"
        "• Мгновенные выплаты\n"
        "• Комиссия с выигрышей: 5-10%\n\n"
        "📞 <b>Поддержка:</b>\n"
        "При возникновении проблем обращайтесь к администраторам."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# Admin panel handlers
@dp.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Handle admin panel return"""
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    if not await is_admin_user(user_id, username):
        await callback.answer("❌ У вас нет прав администратора!")
        return
    
    stats = await db.get_stats()
    commission_rate = await db.get_admin_setting("commission_rate")
    casino_reserve = await db.get_admin_setting("casino_reserve")
    
    admin_text = (
        "👑 <b>Панель администратора</b>\n\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"🎮 Игр сыграно: {stats['total_games']}\n"
        f"💰 Депозитов: ${stats['total_deposited']:.2f}\n"
        f"💸 Выводов: ${stats['total_withdrawn']:.2f}\n"
        f"💵 Прибыль казино: ${stats['casino_profit']:.2f}\n"
        f"📊 Комиссия: {commission_rate}%\n"
        f"🏦 Резерв: ${casino_reserve}"
    )
    
    await callback.message.edit_text(admin_text, reply_markup=create_admin_keyboard(), parse_mode="HTML")
    await callback.answer()

# Register admin handlers
for callback_data, handler in admin_handlers.items():
    dp.callback_query.register(
        lambda c, h=handler: h(c, db) if "state" not in handler.__code__.co_varnames else h(c, state, db),
        F.data == callback_data
    )

for callback_data, handler in coeff_handlers.items():
    dp.callback_query.register(lambda c, h=handler: h(c, db), F.data == callback_data)

# Register edit coefficient handlers
dp.callback_query.register(
    lambda c, state: edit_coefficient_callback(c, state, db),
    F.data.startswith("edit_coeff_")
)

# Register admin state handlers
for state_type, handler in admin_state_handlers.items():
    dp.message.register(lambda m, state, h=handler: h(m, state, db), state_type)

async def main():
    """Main function"""
    # Initialize database
    await db.init_db()
    
    # Add initial admins
    for username in ADMIN_USERNAMES:
        if username.strip():
            # Note: We can't get user_id from username directly,
            # so admins will be added when they first use /admin command
            pass
    
    # Set bot commands
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="admin", description="👑 Панель администратора"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    
    # Start polling
    logger.info("Casino Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())