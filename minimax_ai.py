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
        self.time_limit = 5.0  # 建议设置为 5.0-10.0s，由 try...finally 保证稳定性
        self.start_time = 0

    def get_best_move(self, player_id):
        self.player_id = player_id
        self.opponent_id = 3 - player_id
        self.start_time = time.time()

        # 内存管理：防止置换表过大
        if len(self.transposition_table) > 400000:
            self.transposition_table.clear()

        best_move = None
        last_completed_depth = 0

        # --- 迭代加深 ---
        for current_depth in range(1, self.max_depth + 1):
            try:
                move, score = self._search_at_depth(current_depth)
                if move:
                    best_move = move
                    last_completed_depth = current_depth

                # 发现必胜局直接停止搜索
                if score >= 10000000:
                    break

                # 预留时间缓冲，如果已消耗 80% 时间则不再进入下一层深度的搜索
                if time.time() - self.start_time > self.time_limit * 0.8:
                    break
            except TimeoutError:
                # 某一层深度搜到一半超时，直接跳出循环，使用上一层完整搜出的 best_move
                break

        print(f"\n--- AI 思考简报 ---")
        print(f"位置: {best_move} | 完成深度: {last_completed_depth} | 耗时: {time.time() - self.start_time:.2f}s")
        return best_move

    def _search_at_depth(self, depth):
        """根节点搜索"""
        best_val = -float('inf')
        best_pos = None
        candidates = self._get_candidates()

        # 启发式落子排序：优先搜索中心点附近的点（或结合 evaluator 的 quick_score）
        candidates.sort(key=lambda m: self._quick_evaluate(m[0], m[1]), reverse=True)

        for x, y in candidates:
            # 在进入下一轮模拟前检查时间
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutError

            self.engine.make_move(x, y, self.player_id)
            try:
                # 递归开始
                val = self.minimax(depth - 1, -float('inf'), float('inf'), False)
                if val > best_val:
                    best_val = val
                    best_pos = (x, y)
            finally:
                # 【关键修正】使用 finally 块确保即使发生 TimeoutError，模拟落子也会被撤销
                self.engine.undo_move(x, y)

        return best_pos, best_val

    def minimax(self, depth, alpha, beta, is_maximizing):
        """Alpha-Beta 剪枝递归函数"""
        # 递归内部实时检查超时
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError

        # --- 置换表查询 (TT) ---
        board_hash = self.engine.current_hash
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                if entry['type'] == EXACT: return entry['score']
                if entry['type'] == LOWERBOUND: alpha = max(alpha, entry['score'])
                if entry['type'] == UPPERBOUND: beta = min(beta, entry['score'])
                if alpha >= beta: return entry['score']

        # 终止条件
        if depth == 0:
            return self.evaluator.evaluate_board(self.player_id)

        candidates = self._get_candidates()
        candidates.sort(key=lambda m: self._quick_evaluate(m[0], m[1]), reverse=True)

        original_alpha = alpha
        current_id = self.player_id if is_maximizing else self.opponent_id

        best_score = -float('inf') if is_maximizing else float('inf')

        for x, y in candidates:
            self.engine.make_move(x, y, current_id)
            try:
                # 递归调用
                score = self.minimax(depth - 1, alpha, beta, not is_maximizing)

                if is_maximizing:
                    best_score = max(best_score, score)
                    alpha = max(alpha, score)
                else:
                    best_score = min(best_score, score)
                    beta = min(beta, score)
            finally:
                # 【关键修正】确保回退棋盘状态
                self.engine.undo_move(x, y)

            # Alpha-Beta 剪枝
            if beta <= alpha:
                break

        # 存储结果到置换表并返回
        self._save_tt(board_hash, best_score, depth, original_alpha, beta)
        return best_score

    def _save_tt(self, h, s, d, a, b):
        if s <= a:
            t = UPPERBOUND
        elif s >= b:
            t = LOWERBOUND
        else:
            t = EXACT
        self.transposition_table[h] = {'score': s, 'depth': d, 'type': t}

    def _quick_evaluate(self, x, y):
        """简单的启发式落子排序：优先考虑中心区域"""
        center = self.engine.size // 2
        return (center - abs(x - center)) + (center - abs(y - center))

    def _get_candidates(self):
        """获取已有棋子周围 1-2 格内的空位"""
        candidates = set()
        for x in range(self.engine.size):
            for y in range(self.engine.size):
                if self.engine.board[x][y] != 0:
                    # 搜索半径：1-2格
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.engine.size and 0 <= ny < self.engine.size:
                                if self.engine.board[nx][ny] == 0:
                                    candidates.add((nx, ny))

        # 如果棋盘是空的（开局第一手），下在中心
        if not candidates:
            return [(self.engine.size // 2, self.engine.size // 2)]

        return list(candidates)