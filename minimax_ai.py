import time

# 置换表标记
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class MinimaxAI:
    def __init__(self, engine, evaluator, depth=6):
        self.engine = engine
        self.evaluator = evaluator
        self.max_depth = depth
        self.transposition_table = {}
        self.time_limit = 5.0  # 设定5秒思考限制
        self.start_time = 0

    def get_best_move(self, player_id):
        self.player_id = player_id
        self.opponent_id = 3 - player_id
        self.start_time = time.time()

        # 每一轮开始，清除过期的置换表数据（可选）
        if len(self.transposition_table) > 200000:
            self.transposition_table.clear()

        best_move = None

        # --- 迭代加深 ---
        for current_depth in range(1, self.max_depth + 1):
            try:
                move, score = self._search_at_depth(current_depth)
                if move:
                    best_move = move
                if score >= 10000000: break  # 发现必胜/必堵
                if time.time() - self.start_time > self.time_limit * 0.8: break
            except TimeoutError:
                break

        print(f"\n--- AI 思考简报 ---")
        print(f"位置: {best_move} | 最终深度: {current_depth} | 耗时: {time.time() - self.start_time:.2f}s")
        return best_move

    def _search_at_depth(self, depth):
        best_val = -float('inf')
        best_pos = None
        candidates = self._get_candidates()

        # 快速排序：利用置换表里的历史分数
        candidates.sort(key=lambda m: self._quick_evaluate(m[0], m[1]), reverse=True)

        for x, y in candidates:
            if time.time() - self.start_time > self.time_limit: raise TimeoutError

            self.engine.make_move(x, y, self.player_id)
            val = self.minimax(depth - 1, -float('inf'), float('inf'), False)
            self.engine.undo_move(x, y)

            if val > best_val:
                best_val = val
                best_pos = (x, y)

        return best_pos, best_val

    def minimax(self, depth, alpha, beta, is_maximizing):
        if time.time() - self.start_time > self.time_limit: raise TimeoutError

        # --- 置换表查询 ---
        board_hash = self.engine.current_hash
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                if entry['type'] == EXACT:
                    return entry['score']
                elif entry['type'] == LOWERBOUND:
                    alpha = max(alpha, entry['score'])
                elif entry['type'] == UPPERBOUND:
                    beta = min(beta, entry['score'])
                if alpha >= beta: return entry['score']

        if depth == 0:
            return self.evaluator.evaluate_board(self.player_id)

        candidates = self._get_candidates()
        candidates.sort(key=lambda m: self._quick_evaluate(m[0], m[1]), reverse=True)

        original_alpha = alpha
        if is_maximizing:
            max_eval = -float('inf')
            for x, y in candidates:
                self.engine.make_move(x, y, self.player_id)
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.engine.undo_move(x, y)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break

            self._save_tt(board_hash, max_eval, depth, original_alpha, beta)
            return max_eval
        else:
            min_eval = float('inf')
            for x, y in candidates:
                self.engine.make_move(x, y, self.opponent_id)
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.engine.undo_move(x, y)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break

            self._save_tt(board_hash, min_eval, depth, original_alpha, beta)
            return min_eval

    def _save_tt(self, h, s, d, a, b):
        if s <= a:
            t = UPPERBOUND
        elif s >= b:
            t = LOWERBOUND
        else:
            t = EXACT
        self.transposition_table[h] = {'score': s, 'depth': d, 'type': t}

    def _quick_evaluate(self, x, y):
        # 简单的启发式落子排序
        center = self.engine.size // 2
        return (center - abs(x - center)) + (center - abs(y - center))

    def _get_candidates(self):
        # ... 原有的扩展范围逻辑 ...
        candidates = set()
        for x in range(self.engine.size):
            for y in range(self.engine.size):
                if self.engine.board[x][y] != 0:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.engine.size and 0 <= ny < self.engine.size:
                                if self.engine.board[nx][ny] == 0:
                                    candidates.add((nx, ny))
        return list(candidates) if candidates else [(self.engine.size // 2, self.engine.size // 2)]