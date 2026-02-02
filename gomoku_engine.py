# Author: Hu Jia
# Date:

import numpy as np


class GomokuEngine:
    def __init__(self, size=15):
        self.size = size
        # 初始化 15x15 棋盘，0:空, 1:黑子, 2:白子
        self.board = np.zeros((size, size), dtype=int)
        # 记录最近一次落子坐标，用于胜负检查优化
        self.last_move = None

    def is_valid_move(self, x, y):
        """检查落子是否合法"""
        return 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == 0

    def make_move(self, x, y, player):
        """落子逻辑"""
        if self.is_valid_move(x, y):
            self.board[x][y] = player
            self.last_move = (x, y)
            return True
        return False

    def check_win(self, x, y, player):
        """
        胜负判定：检查刚落子的坐标 (x, y) 在四个方向上是否有连续5个子
        """
        directions = [
            (1, 0),  # 水平
            (0, 1),  # 垂直
            (1, 1),  # 主对角线
            (1, -1)  # 副对角线
        ]

        for dx, dy in directions:
            count = 1
            # 正向搜索
            tx, ty = x + dx, y + dy
            while 0 <= tx < self.size and 0 <= ty < self.size and self.board[tx][ty] == player:
                count += 1
                tx += dx
                ty += dy
            # 反向搜索
            tx, ty = x - dx, y - dy
            while 0 <= tx < self.size and 0 <= ty < self.size and self.board[tx][ty] == player:
                count += 1
                tx -= dx
                ty -= dy

            if count >= 5:
                return True
        return False

    def reset(self):
        """重置棋盘"""
        self.board.fill(0)
        self.last_move = None