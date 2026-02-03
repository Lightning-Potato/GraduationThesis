# Author: Hu Jia
# Date:

import numpy as np
import random


class GreedyAI:
    def __init__(self, engine, player_id):
        self.engine = engine
        self.player_id = player_id
        self.opponent_id = 3 - player_id  # 如果AI是1，对手就是2；反之亦然

    def evaluate_point(self, x, y, player):
        """
        简单的评估函数：计算在 (x,y) 处落子后，四个方向上连续相同棋子的最大数量
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        max_count = 0

        for dx, dy in directions:
            count = 1
            # 正向探测
            tx, ty = x + dx, y + dy
            while 0 <= tx < self.engine.size and 0 <= ty < self.engine.size and self.engine.board[tx][ty] == player:
                count += 1
                tx += dx
                ty += dy
            # 反向探测
            tx, ty = x - dx, y - dy
            while 0 <= tx < self.engine.size and 0 <= ty < self.engine.size and self.engine.board[tx][ty] == player:
                count += 1
                tx -= dx
                ty -= dy
            max_count = max(max_count, count)
        return max_count

    def get_best_move(self):
        """
        贪心策略：优先找能让自己连成最长线条的位置；
        如果没有必胜点，则优先封堵对手连成最长线条的位置。
        """
        best_score = -1
        best_moves = []

        for x in range(self.engine.size):
            for y in range(self.engine.size):
                if self.engine.is_valid_move(x, y):
                    # 1. 进攻分数：落子后我的最长连珠
                    my_score = self.evaluate_point(x, y, self.player_id)
                    # 2. 防御分数：落子后对手的最长连珠（封堵意义）
                    opp_score = self.evaluate_point(x, y, self.opponent_id)

                    # 综合评分：进攻权重略高于防御，如果能连成5个，权重最高
                    current_score = max(my_score * 1.1, opp_score)

                    if current_score > best_score:
                        best_score = current_score
                        best_moves = [(x, y)]
                    elif current_score == best_score:
                        best_moves.append((x, y))

        # 如果有多个分值相同的点，随机选一个增加灵活性
        return random.choice(best_moves) if best_moves else None