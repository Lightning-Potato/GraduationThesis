# Author: Hu Jia
# Date:

import random
from evaluator import GomokuEvaluator, SCORES, PATTERNS  # 确保文件名对应


class GreedyAI:
    def __init__(self, engine, player_id):
        self.engine = engine
        self.player_id = player_id
        self.opponent_id = 3 - player_id
        # 初始化我们刚刚写好的高级评估器
        self.evaluator = GomokuEvaluator(engine)

    def get_best_move(self):
        """
        升级版贪心策略：
        遍历所有空位，模拟落子，利用全局评估函数找分值最高的位置。
        """
        best_score = -float('inf')
        best_moves = []

        # 优化搜索范围：只考虑已有棋子周围的空位（可选，能大幅提升速度）
        search_range = self._get_candidates()

        for x, y in search_range:
            # 1. 模拟落子
            self.engine.make_move(x, y, self.player_id)

            # 2. 检查是否直接获胜（最高优先级）
            if self.engine.check_win(x, y, self.player_id):
                self.engine.undo_move(x, y)
                return (x, y)

            # 3. 评估当前棋盘局势
            # 这个分数已经包含了 (己方分 - 对方分)
            current_score = self.evaluator.evaluate_board(self.player_id)

            # 4. 撤销模拟落子
            self.engine.undo_move(x, y)

            if current_score > best_score:
                best_score = current_score
                best_moves = [(x, y)]
            elif current_score == best_score:
                best_moves.append((x, y))

        return random.choice(best_moves) if best_moves else None

    def _get_candidates(self):
        """
        获取待选搜索点：为了提速，只搜索已有棋子周围2格范围内的空位。
        如果棋盘全空，则返回中心点。
        """
        candidates = set()
        has_any_piece = False
        for x in range(self.engine.size):
            for y in range(self.engine.size):
                if self.engine.board[x][y] != 0:
                    has_any_piece = True
                    # 检查周围2格
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.engine.size and 0 <= ny < self.engine.size:
                                if self.engine.board[nx][ny] == 0:
                                    candidates.add((nx, ny))

        if not has_any_piece:
            return [(self.engine.size // 2, self.engine.size // 2)]
        return list(candidates)