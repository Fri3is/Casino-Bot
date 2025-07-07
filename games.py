from typing import Dict, List, Tuple, Optional
import random

class GameLogic:
    """Game logic for casino games"""
    
    # Game type constants
    DICE = "dice"
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    DARTS = "darts"
    BOWLING = "bowling"
    SLOTS = "slots"
    
    # Dice game results mapping
    DICE_EMOJI = "🎲"
    FOOTBALL_EMOJI = "⚽"
    BASKETBALL_EMOJI = "🏀"
    DARTS_EMOJI = "🎯"
    BOWLING_EMOJI = "🎳"
    SLOTS_EMOJI = "🎰"
    
    @staticmethod
    def check_dice_bet(dice_value: int, bet_type: str, dice_value2: int = None) -> bool:
        """Check if dice bet wins"""
        if bet_type == "even":
            return dice_value % 2 == 0
        elif bet_type == "odd":
            return dice_value % 2 == 1
        elif bet_type == "greater_3":
            return dice_value > 3
        elif bet_type == "less_4":
            return dice_value < 4
        elif bet_type.startswith("number_"):
            target_number = int(bet_type.split("_")[1])
            return dice_value == target_number
        elif bet_type == "sum_greater_7" and dice_value2:
            return (dice_value + dice_value2) > 7
        elif bet_type == "sum_less_7" and dice_value2:
            return (dice_value + dice_value2) < 7
        elif bet_type == "sum_equals_7" and dice_value2:
            return (dice_value + dice_value2) == 7
        elif bet_type.startswith("product_") and dice_value2:
            product = dice_value * dice_value2
            if bet_type == "product_1_18":
                return 1 <= product <= 18
            elif bet_type == "product_19_36":
                return 19 <= product <= 36
        return False
    
    @staticmethod
    def check_football_bet(football_value: int, bet_type: str) -> bool:
        """Check if football bet wins"""
        # Football values: 1-3 = miss, 4-5 = goal, 6 = goal in top right corner
        if bet_type == "goal":
            return football_value >= 4
        elif bet_type == "miss":
            return football_value <= 3
        elif bet_type == "top_right":
            return football_value == 6
        return False
    
    @staticmethod
    def check_basketball_bet(basketball_value: int, bet_type: str) -> bool:
        """Check if basketball bet wins"""
        # Basketball values: 1-2 = miss, 3 = goal with bounce, 4-5 = clean goal, 6 = stuck between ring and backboard
        if bet_type == "goal":
            return basketball_value >= 3
        elif bet_type == "miss":
            return basketball_value <= 2
        elif bet_type == "clean_goal":
            return basketball_value in [4, 5]
        elif bet_type == "bounce":
            return basketball_value == 3
        elif bet_type == "stuck":
            return basketball_value == 6
        return False
    
    @staticmethod
    def check_darts_bet(darts_value: int, bet_type: str) -> bool:
        """Check if darts bet wins"""
        # Darts values: 1-2 = miss/bounce, 3-4 = white sector, 5-6 = red sector/center
        if bet_type == "white":
            return darts_value in [3, 4]
        elif bet_type == "red":
            return darts_value in [5, 6]
        elif bet_type == "center":
            return darts_value == 6
        elif bet_type == "bounce":
            return darts_value in [1, 2]
        elif bet_type == "better":
            # For "better" game, higher value = better (closer to center)
            return True  # Always wins something, coefficient depends on value
        return False
    
    @staticmethod
    def check_bowling_bet(bowling_value: int, bet_type: str) -> bool:
        """Check if bowling bet wins"""
        # Bowling values: 1-2 = 0 pins, 3-4 = few pins, 5-6 = strike
        if bet_type == "strike":
            return bowling_value in [5, 6]
        elif bet_type == "zero":
            return bowling_value in [1, 2]
        elif bet_type == "better":
            # For "better" game, higher value = more pins
            return True  # Always wins something, coefficient depends on value
        return False
    
    @staticmethod
    def check_slots_bet(slots_value: int, bet_type: str) -> bool:
        """Check if slots bet wins"""
        # Slots values interpretation (simplified)
        if bet_type == "exact_value":
            return True  # Need to specify exact value in advanced implementation
        elif bet_type == "jackpot":
            # Jackpot = three identical symbols (values 43, 22, 1, 64)
            return slots_value in [43, 22, 1, 64]
        elif bet_type == "mini_jackpot":
            # Mini jackpot = two identical symbols nearby
            return slots_value in [6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61]
        return False
    
    @staticmethod
    def get_dice_bet_options() -> Dict[str, str]:
        """Get dice betting options with descriptions"""
        return {
            "even": "Четное число",
            "odd": "Нечетное число", 
            "greater_3": "Больше 3",
            "less_4": "Меньше 4",
            "number_1": "Число 1",
            "number_2": "Число 2",
            "number_3": "Число 3",
            "number_4": "Число 4",
            "number_5": "Число 5",
            "number_6": "Число 6",
            "sum_greater_7": "Сумма > 7 (два кубика)",
            "sum_less_7": "Сумма < 7 (два кубика)",
            "sum_equals_7": "Сумма = 7 (два кубика)",
            "product_1_18": "Произведение 1-18",
            "product_19_36": "Произведение 19-36"
        }
    
    @staticmethod
    def get_football_bet_options() -> Dict[str, str]:
        """Get football betting options with descriptions"""
        return {
            "goal": "Гол",
            "miss": "Промах",
            "top_right": "Правый верхний угол"
        }
    
    @staticmethod
    def get_basketball_bet_options() -> Dict[str, str]:
        """Get basketball betting options with descriptions"""
        return {
            "goal": "Гол",
            "miss": "Промах",
            "clean_goal": "Чистый гол",
            "bounce": "Отскок от кольца",
            "stuck": "Застревание мяча"
        }
    
    @staticmethod
    def get_darts_bet_options() -> Dict[str, str]:
        """Get darts betting options with descriptions"""
        return {
            "white": "Белый сектор",
            "red": "Красный сектор", 
            "center": "Центр",
            "bounce": "Отскок дротика",
            "better": "Игра 'лучше'"
        }
    
    @staticmethod
    def get_bowling_bet_options() -> Dict[str, str]:
        """Get bowling betting options with descriptions"""
        return {
            "strike": "Страйк",
            "zero": "Ни одной кегли",
            "better": "Игра 'лучше'"
        }
    
    @staticmethod
    def get_slots_bet_options() -> Dict[str, str]:
        """Get slots betting options with descriptions"""
        return {
            "exact_value": "Угадай значение",
            "jackpot": "Джекпот (3 одинаковых)",
            "mini_jackpot": "Мини джекпот (2 рядом)"
        }
    
    @staticmethod
    def get_all_bet_options() -> Dict[str, Dict[str, str]]:
        """Get all betting options for all games"""
        return {
            GameLogic.DICE: GameLogic.get_dice_bet_options(),
            GameLogic.FOOTBALL: GameLogic.get_football_bet_options(),
            GameLogic.BASKETBALL: GameLogic.get_basketball_bet_options(),
            GameLogic.DARTS: GameLogic.get_darts_bet_options(),
            GameLogic.BOWLING: GameLogic.get_bowling_bet_options(),
            GameLogic.SLOTS: GameLogic.get_slots_bet_options()
        }
    
    @staticmethod
    def check_bet_result(game_type: str, result_value: int, bet_type: str, 
                        result_value2: int = None) -> bool:
        """Universal function to check bet result"""
        if game_type == GameLogic.DICE:
            return GameLogic.check_dice_bet(result_value, bet_type, result_value2)
        elif game_type == GameLogic.FOOTBALL:
            return GameLogic.check_football_bet(result_value, bet_type)
        elif game_type == GameLogic.BASKETBALL:
            return GameLogic.check_basketball_bet(result_value, bet_type)
        elif game_type == GameLogic.DARTS:
            return GameLogic.check_darts_bet(result_value, bet_type)
        elif game_type == GameLogic.BOWLING:
            return GameLogic.check_bowling_bet(result_value, bet_type)
        elif game_type == GameLogic.SLOTS:
            return GameLogic.check_slots_bet(result_value, bet_type)
        return False
    
    @staticmethod
    def get_better_coefficient(game_type: str, result_value: int, base_coefficient: float) -> float:
        """Calculate coefficient for 'better' type games"""
        if game_type == GameLogic.DARTS and result_value == 6:
            return base_coefficient * 3  # Center hit = 3x multiplier
        elif game_type == GameLogic.DARTS and result_value in [5, 4]:
            return base_coefficient * 2  # Close to center = 2x multiplier
        elif game_type == GameLogic.DARTS and result_value == 3:
            return base_coefficient * 1.5  # Hit but not close = 1.5x multiplier
        elif game_type == GameLogic.BOWLING:
            if result_value in [5, 6]:  # Strike
                return base_coefficient * 3
            elif result_value in [3, 4]:  # Some pins
                return base_coefficient * 1.5
        
        return base_coefficient
    
    @staticmethod
    def get_game_emoji(game_type: str) -> str:
        """Get emoji for game type"""
        emojis = {
            GameLogic.DICE: GameLogic.DICE_EMOJI,
            GameLogic.FOOTBALL: GameLogic.FOOTBALL_EMOJI,
            GameLogic.BASKETBALL: GameLogic.BASKETBALL_EMOJI,
            GameLogic.DARTS: GameLogic.DARTS_EMOJI,
            GameLogic.BOWLING: GameLogic.BOWLING_EMOJI,
            GameLogic.SLOTS: GameLogic.SLOTS_EMOJI
        }
        return emojis.get(game_type, "🎮")