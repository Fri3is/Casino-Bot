import aiosqlite
import asyncio
from typing import Optional, Dict, List, Tuple
import os
from datetime import datetime

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database with all necessary tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance REAL DEFAULT 0.0,
                    total_deposited REAL DEFAULT 0.0,
                    total_withdrawn REAL DEFAULT 0.0,
                    total_won REAL DEFAULT 0.0,
                    total_lost REAL DEFAULT 0.0,
                    games_played INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned BOOLEAN DEFAULT FALSE
                )
            ''')

            # Game settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS game_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_type TEXT NOT NULL,
                    bet_type TEXT NOT NULL,
                    coefficient REAL NOT NULL,
                    min_bet REAL DEFAULT 1.0,
                    max_bet REAL DEFAULT 1000.0,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Admin settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admin_settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL
                )
            ''')

            # Game history table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_type TEXT,
                    bet_type TEXT,
                    bet_amount REAL,
                    result_value INTEGER,
                    won BOOLEAN,
                    win_amount REAL DEFAULT 0.0,
                    commission REAL DEFAULT 0.0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Transactions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    transaction_type TEXT, -- 'deposit', 'withdrawal', 'bet', 'win'
                    amount REAL,
                    cryptopay_invoice_id TEXT,
                    status TEXT DEFAULT 'pending',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Admin users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await self._init_default_settings(db)
            await db.commit()

    async def _init_default_settings(self, db):
        """Initialize default game settings and admin settings"""
        
        # Check if settings already exist
        cursor = await db.execute("SELECT COUNT(*) FROM game_settings")
        count = await cursor.fetchone()
        if count[0] > 0:
            return

        # Default game settings
        default_settings = [
            # Dice games
            ('dice', 'even', 1.9),
            ('dice', 'odd', 1.9),
            ('dice', 'greater_3', 1.9),
            ('dice', 'less_4', 1.9),
            ('dice', 'number_1', 5.5),
            ('dice', 'number_2', 5.5),
            ('dice', 'number_3', 5.5),
            ('dice', 'number_4', 5.5),
            ('dice', 'number_5', 5.5),
            ('dice', 'number_6', 5.5),
            ('dice', 'sum_greater_7', 1.7),
            ('dice', 'sum_less_7', 1.7),
            ('dice', 'sum_equals_7', 5.0),
            
            # Football
            ('football', 'goal', 3.5),
            ('football', 'miss', 1.3),
            ('football', 'top_right', 15.0),
            
            # Basketball
            ('basketball', 'goal', 2.2),
            ('basketball', 'miss', 1.7),
            ('basketball', 'clean_goal', 4.5),
            ('basketball', 'bounce', 8.0),
            ('basketball', 'stuck', 25.0),
            
            # Darts
            ('darts', 'white', 2.0),
            ('darts', 'red', 3.0),
            ('darts', 'center', 6.0),
            ('darts', 'bounce', 10.0),
            
            # Bowling
            ('bowling', 'strike', 8.0),
            ('bowling', 'zero', 3.0),
            
            # Slots
            ('slots', 'jackpot', 50.0),
            ('slots', 'mini_jackpot', 8.0),
            ('slots', 'exact_value', 25.0),
        ]

        for game_type, bet_type, coefficient in default_settings:
            await db.execute(
                "INSERT INTO game_settings (game_type, bet_type, coefficient) VALUES (?, ?, ?)",
                (game_type, bet_type, coefficient)
            )

        # Default admin settings
        admin_settings = [
            ('commission_rate', '7'),  # 7% commission
            ('min_deposit', '1'),
            ('min_withdrawal', '5'),
            ('max_bet_multiplier', '100'),
            ('casino_reserve', '0'),
        ]

        for setting_name, setting_value in admin_settings:
            await db.execute(
                "INSERT OR REPLACE INTO admin_settings (setting_name, setting_value) VALUES (?, ?)",
                (setting_name, setting_value)
            )

    # User operations
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_user(self, user_id: int, username: str = None, first_name: str = None):
        """Create new user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, first_name)
            )
            await db.commit()

    async def update_user_balance(self, user_id: int, amount: float) -> bool:
        """Update user balance"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_user_balance(self, user_id: int) -> float:
        """Get user balance"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return row[0] if row else 0.0

    # Game settings operations
    async def get_game_settings(self, game_type: str = None) -> List[Dict]:
        """Get game settings"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if game_type:
                cursor = await db.execute(
                    "SELECT * FROM game_settings WHERE game_type = ? AND is_active = TRUE",
                    (game_type,)
                )
            else:
                cursor = await db.execute("SELECT * FROM game_settings WHERE is_active = TRUE")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_coefficient(self, game_type: str, bet_type: str, coefficient: float):
        """Update game coefficient"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE game_settings SET coefficient = ? WHERE game_type = ? AND bet_type = ?",
                (coefficient, game_type, bet_type)
            )
            await db.commit()

    # Admin settings operations
    async def get_admin_setting(self, setting_name: str) -> str:
        """Get admin setting value"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT setting_value FROM admin_settings WHERE setting_name = ?",
                (setting_name,)
            )
            row = await cursor.fetchone()
            return row[0] if row else "0"

    async def update_admin_setting(self, setting_name: str, setting_value: str):
        """Update admin setting"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO admin_settings (setting_name, setting_value) VALUES (?, ?)",
                (setting_name, setting_value)
            )
            await db.commit()

    # Game history operations
    async def add_game_record(self, user_id: int, game_type: str, bet_type: str, 
                            bet_amount: float, result_value: int, won: bool, 
                            win_amount: float = 0.0, commission: float = 0.0):
        """Add game record to history"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO game_history 
                (user_id, game_type, bet_type, bet_amount, result_value, won, win_amount, commission)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, game_type, bet_type, bet_amount, result_value, won, win_amount, commission))
            
            # Update user statistics
            if won:
                await db.execute(
                    "UPDATE users SET total_won = total_won + ?, games_played = games_played + 1 WHERE user_id = ?",
                    (win_amount, user_id)
                )
            else:
                await db.execute(
                    "UPDATE users SET total_lost = total_lost + ?, games_played = games_played + 1 WHERE user_id = ?",
                    (bet_amount, user_id)
                )
            
            await db.commit()

    # Transaction operations
    async def add_transaction(self, user_id: int, transaction_type: str, amount: float, 
                            cryptopay_invoice_id: str = None, status: str = 'pending'):
        """Add transaction record"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO transactions 
                (user_id, transaction_type, amount, cryptopay_invoice_id, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, transaction_type, amount, cryptopay_invoice_id, status))
            await db.commit()

    # Admin users operations
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM admin_users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return row is not None

    async def add_admin(self, user_id: int, username: str, added_by: int):
        """Add admin user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO admin_users (user_id, username, added_by) VALUES (?, ?, ?)",
                (user_id, username, added_by)
            )
            await db.commit()

    async def get_stats(self) -> Dict:
        """Get casino statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total users
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await cursor.fetchone())[0]
            
            # Total games played
            cursor = await db.execute("SELECT COUNT(*) FROM game_history")
            total_games = (await cursor.fetchone())[0]
            
            # Total deposited
            cursor = await db.execute("SELECT SUM(total_deposited) FROM users")
            total_deposited = (await cursor.fetchone())[0] or 0
            
            # Total withdrawn
            cursor = await db.execute("SELECT SUM(total_withdrawn) FROM users")
            total_withdrawn = (await cursor.fetchone())[0] or 0
            
            # Casino profit
            cursor = await db.execute("SELECT SUM(commission) FROM game_history")
            casino_profit = (await cursor.fetchone())[0] or 0
            
            return {
                'total_users': total_users,
                'total_games': total_games,
                'total_deposited': total_deposited,
                'total_withdrawn': total_withdrawn,
                'casino_profit': casino_profit
            }