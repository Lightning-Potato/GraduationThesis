# Author: Hu Jia
# Date:

import numpy as np
import random

import numpy as np


class GomokuEngine:
    def __init__(self, size=15):
        self.size = size
        # 0: 空, 1: 黑子 (先手), 2: 白子
        self.board = np.zeros((size, size), dtype=int)
        self.last_move = None

        # --- Zobrist Hashing 初始化 ---
        # 为棋盘每一个格子(size*size)的每种状态(3种：空、黑、白)生成一个随机的64位整数
        # np.uint64 确保哈希值范围足够大，减少哈希碰撞
        self.zobrist_table = np.random.randint(0, 2 ** 63, size=(size, size, 3), dtype=np.uint64)
        # 初始化当前棋盘的哈希值
        self.current_hash = self._calculate_full_hash()

    def _calculate_full_hash(self):
        """计算初始状态（全空）的完整哈希值"""
        h = np.uint64(0)
        for x in range(self.size):
            for y in range(self.size):
                # 初始状态每个格子都是 0 (空)
                h ^= self.zobrist_table[x][y][0]
        return h

    def is_valid_move(self, x, y):
        """检查坐标是否在棋盘内且为空"""
        return 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == 0

    def make_move(self, x, y, player):
        """落子并同步更新 Zobrist 哈希值"""
        if self.is_valid_move(x, y):
            # 1. 在哈希值中通过异或(XOR)移除该位置的“空”状态
            self.current_hash ^= self.zobrist_table[x][y][0]

            # 2. 更新棋盘数组
            self.board[x][y] = player
            self.last_move = (x, y)

            # 3. 在哈希值中通过异或(XOR)加入该位置的新棋子状态
            self.current_hash ^= self.zobrist_table[x][y][player]
            return True
        return False

    def undo_move(self, x, y):
        """
        回滚落子（对 AI 搜索极其重要）：
        将棋子变回空位，并同步更新哈希值
        """
        player = self.board[x][y]
        if player != 0:
            # 1. 移除棋子状态
            self.current_hash ^= self.zobrist_table[x][y][player]
            # 2. 恢复空状态
            self.board[x][y] = 0
            self.current_hash ^= self.zobrist_table[x][y][0]
            self.last_move = None  # 注意：简单起见，undo 后 last_move 不再记录

    def check_win(self, x, y, player):
        """检查当前落子位置是否达成五连"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            # 正向探索
            tx, ty = x + dx, y + dy
            while 0 <= tx < self.size and 0 <= ty < self.size and self.board[tx][ty] == player:
                count += 1
                tx += dx
                ty += dy
            # 反向探索
            tx, ty = x - dx, y - dy
            while 0 <= tx < self.size and 0 <= ty < self.size and self.board[tx][ty] == player:
                count += 1
                tx -= dx
                ty -= dy
            if count >= 5:
                return True
        return False

    def reset(self):
        """重置棋盘并重新初始化哈希"""
        self.board.fill(0)
        self.last_move = None
        self.current_hash = self._calculate_full_hash()