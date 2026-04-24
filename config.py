# Author: Hu Jia
# Date:

"""
config.py
"""

# --- Chessboard and Game Settings ---
BOARD_SIZE = 15
WINDOW_SIZE = 600
GRID_SIZE = WINDOW_SIZE // (BOARD_SIZE + 1)
MARGIN = 40
BOTTOM_PANEL = 80
SCREEN_SIZE = GRID_SIZE * (BOARD_SIZE - 1) + MARGIN * 2
WINDOW_HEIGHT = SCREEN_SIZE + BOTTOM_PANEL

# --- UI Color Scheme ---
COLORS = {
    'BACKGROUND': (235, 185, 120),
    'BLACK': (30, 30, 30),
    'WHITE': (245, 245, 245),
    'TEXT_COLOR': (20, 20, 20),
    'BUTTON_COLOR': (200, 160, 100),
    'BUTTON_HOVER': (220, 180, 120),

    'LINE': (0, 0, 0),
    'LAST_MOVE': (255, 0, 0),       # The color used to mark the last move
}

# --- AI Engine Parameters ---
AI_CONFIG = {
    'MAX_DEPTH': 6,                 # Search depth limit
    'TIME_LIMIT': 10.0,             # AI Thinking Time Limit (seconds)
    'TT_SIZE_LIMIT': 400000,        # Maximum number of entries in the replacement table
}

# --- Heuristic Weights --- # Unified management of scores for easier subsequent numerical tuning experiments
BOARD_SCORES = {
    'FIVE': 100000000,
    'ALIVE_FOUR': 10000000,
    'DEAD_FOUR': 1000000,
    'ALIVE_THREE': 100000,
    'DEAD_THREE': 10000,
    'ALIVE_TWO': 1000,
    'DEAD_TWO': 100,

    'DEFENSE_MULTIPLIER': 1.2       # Defense weighting
}