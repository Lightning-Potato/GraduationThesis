# Author: Hu Jia
# Date:

import random


class MinimaxAI:
    def __init__(self, engine, evaluator, depth=3):
        self.engine = engine
        self.evaluator = evaluator
        self.max_depth = depth
        self.player_id = 0
        self.opponent_id = 0
        # --- 新增：置换表 (Transposition Table) ---
        self.transposition_table = {}

    def get_best_move(self, player_id):
        self.player_id = player_id
        self.opponent_id = 3 - player_id

        # 每一大步开始前清空置换表，或者保留它（取决于内存和棋局变化）
        self.transposition_table = {}

        best_val = -float('inf')
        best_move = None
        candidates = self._get_candidates()

        for x, y in candidates:
            self.engine.make_move(x, y, self.player_id)
            # 传入当前的 alpha 和 beta
            move_val = self.minimax(self.max_depth - 1, -float('inf'), float('inf'), False)
            self.engine.undo_move(x, y)

            if move_val > best_val:
                best_val = move_val
                best_move = (x, y)

        return best_move

    def minimax(self, depth, alpha, beta, is_maximizing):
        # --- 1. 查表：如果这个局面（Hash）我们算过，且深度足够，直接返回 ---
        board_hash = self.engine.current_hash
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']

        # 2. 终止条件
        if depth == 0:
            score = self.evaluator.evaluate_board(self.player_id)
            # 记录结果到置换表
            self.transposition_table[board_hash] = {'score': score, 'depth': depth}
            return score

        candidates = self._get_candidates()

        if is_maximizing:
            max_eval = -float('inf')
            for x, y in candidates:
                self.engine.make_move(x, y, self.player_id)
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.engine.undo_move(x, y)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            # 记录搜索结果
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
                if beta <= alpha:
                    break
            # 记录搜索结果
            self.transposition_table[board_hash] = {'score': min_eval, 'depth': depth}
            return min_eval

    def _get_candidates(self):
        """复用之前的逻辑：只搜索棋子周围空位"""
        candidates = set()
        board = self.engine.board
        has_piece = False
        for x in range(self.engine.size):
            for y in range(self.engine.size):
                if board[x][y] != 0:
                    has_piece = True
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.engine.size and 0 <= ny < self.engine.size:
                                if board[nx][ny] == 0:
                                    candidates.add((nx, ny))
        if not has_piece:
            return [(self.engine.size // 2, self.engine.size // 2)]
        return list(candidates)