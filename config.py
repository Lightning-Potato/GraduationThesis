# Author: Hu Jia
# Date:

"""
config.py
用于统一管理游戏参数，提高系统的可维护性 (Maintainability)。
"""

# --- 棋盘与游戏设置 ---
BOARD_SIZE = 15
WINDOW_SIZE = 600
GRID_SIZE = WINDOW_SIZE // (BOARD_SIZE + 1)
MARGIN = 40
BOTTOM_PANEL = 80
SCREEN_SIZE = GRID_SIZE * (BOARD_SIZE - 1) + MARGIN * 2
WINDOW_HEIGHT = SCREEN_SIZE + BOTTOM_PANEL

# --- UI 颜色配置 ---
COLORS = {
    'BACKGROUND': (235, 185, 120),
    'BLACK': (30, 30, 30),
    'WHITE': (245, 245, 245),
    'TEXT_COLOR': (20, 20, 20),
    'BUTTON_COLOR': (200, 160, 100),
    'BUTTON_HOVER': (220, 180, 120),

    'LINE': (0, 0, 0),
    'LAST_MOVE': (255, 0, 0),       # 最后落子的标记颜色
}

# --- AI 引擎参数 ---
AI_CONFIG = {
    'MAX_DEPTH': 6,                 # 搜索深度限制
    'TIME_LIMIT': 10.0,             # AI 思考限时（秒）
    'TT_SIZE_LIMIT': 400000,        # 置换表条目上限
}

# --- 启发式分值权重 (Heuristic Weights) ---
# 统一管理分值，方便后续进行“数值调优”实验
BOARD_SCORES = {
    'FIVE': 100000000,
    'ALIVE_FOUR': 10000000,
    'DEAD_FOUR': 1000000,
    'ALIVE_THREE': 100000,
    'DEAD_THREE': 10000,
    'ALIVE_TWO': 1000,
    'DEAD_TWO': 100,

    'DEFENSE_MULTIPLIER': 1.2       # 防御分权重
}