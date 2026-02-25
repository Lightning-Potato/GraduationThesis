# Author: Hu Jia
# Date: 2026-02-25
# Refined for Alpha-Beta efficiency and Move-ordering [cite: 18, 36]

import random


class MinimaxAI:
    def __init__(self, engine, evaluator, depth=3):
        self.engine = engine
        self.evaluator = evaluator
        self.max_depth = depth
        self.transposition_table = {}

    def get_best_move(self, player_id):
        self.player_id = player_id
        self.opponent_id = 3 - player_id
        self.transposition_table = {}

        best_move = None
        move_scores = []

        # 1. 获取候选点并进行简单的启发式排序 (Move-ordering)
        candidates = self._get_candidates()

        # 这里的排序是关键：先进行一层浅显的评估，让好的落子点排在前面
        # 这样 Alpha-Beta 就能更早地剪掉坏的分支 [cite: 12, 59]
        candidates.sort(key=lambda m: self._quick_evaluate(m[0], m[1]), reverse=True)

        for x, y in candidates:
            self.engine.make_move(x, y, self.player_id)
            # 执行 Alpha-Beta 搜索
            val = self.minimax(self.max_depth - 1, -float('inf'), float('inf'), False)
            self.engine.undo_move(x, y)
            move_scores.append(((x, y), val))

        move_scores.sort(key=lambda x: x[1], reverse=True)

        print("\n--- AI 思考简报 (优化版) ---")
        for m, s in move_scores[:3]:
            print(f"位置 {m} | 预估评分: {s}")

        return move_scores[0][0]

    def minimax(self, depth, alpha, beta, is_maximizing):
        # 使用 Zobrist Hash 检查置换表
        board_hash = self.engine.current_hash
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']

        if depth == 0:
            return self.evaluator.evaluate_board(self.player_id)

        candidates = self._get_candidates()
        # 在每一层也进行排序能极大提升剪枝效率 [cite: 36, 59]
        candidates.sort(key=lambda m: self._quick_evaluate(m[0], m[1]), reverse=True)

        if is_maximizing:
            max_eval = -float('inf')
            for x, y in candidates:
                self.engine.make_move(x, y, self.player_id)
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.engine.undo_move(x, y)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break  # Alpha-Beta 剪枝
            self.transposition_table[board_hash] = {'score': max_eval, 'depth': depth}
            return max_eval
        else:
            min_eval = float('inf')
            for x, y in candidates:
                self.engine.make_move(x, y, self.opponent_id)
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.engine.undo_move(x, y)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break  # Alpha-Beta 剪枝
            self.transposition_table[board_hash] = {'score': min_eval, 'depth': depth}
            return min_eval

    def _quick_evaluate(self, x, y):
        """简单的启发式评分，用于落子排序。优先考虑中心和邻近位置"""
        center = self.engine.size // 2
        dist_score = (center - abs(x - center)) + (center - abs(y - center))
        return dist_score

    def _get_candidates(self):
        """扩展搜索范围：已有棋子周围 1-2 格 """
        candidates = set()
        board = self.engine.board
        occupied = []

        for x in range(self.engine.size):
            for y in range(self.engine.size):
                if board[x][y] != 0:
                    occupied.append((x, y))

        if not occupied:
            return [(self.engine.size // 2, self.engine.size // 2)]

        for x, y in occupied:
            # 搜索半径：1格通常足够，2格更稳健但慢 [cite: 35]
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.engine.size and 0 <= ny < self.engine.size:
                        if board[nx][ny] == 0:
                            candidates.add((nx, ny))
        return list(candidates)