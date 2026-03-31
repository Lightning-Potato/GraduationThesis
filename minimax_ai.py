import time
import numpy as np

# 置换表状态标记
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class MinimaxAI:
    def __init__(self, engine, evaluator, depth=6):
        self.engine = engine
        self.evaluator = evaluator
        self.max_depth = depth
        self.transposition_table = {}
        self.time_limit = 10.0  # 最大思考时间限制
        self.start_time = 0

    def get_best_move(self, player_id):
        self.player_id = player_id
        self.opponent_id = 3 - player_id

        # --- 优化：开局库策略 ---
        # 如果棋盘全空，直接下中心位置，不浪费算力
        if np.sum(self.engine.board != 0) == 0:
            return (self.engine.size // 2, self.engine.size // 2)

        self.start_time = time.time()

        # 定期清理置换表防止内存溢出
        if len(self.transposition_table) > 400000:
            self.transposition_table.clear()

        best_move = None
        last_completed_depth = 0

        # --- 核心逻辑：迭代加深搜索 ---
        for current_depth in range(1, self.max_depth + 1):
            try:
                move, score = self._search_at_depth(current_depth)
                if move:
                    best_move = move
                    last_completed_depth = current_depth

                # 必胜剪枝：一旦发现必胜路径则停止加深搜索
                if score >= 10000000: break

                # 时间预警：如果已经消耗 80% 时间，则不开启下一层深度
                if time.time() - self.start_time > self.time_limit * 0.8: break
            except TimeoutError:
                break

        print(f"\n--- AI 思考简报 ---")
        print(f"位置: {best_move} | 最终深度: {last_completed_depth} | 耗时: {time.time() - self.start_time:.2f}s")
        return best_move

    def _search_at_depth(self, depth):
        """根节点搜索逻辑"""
        best_val = -float('inf')
        best_pos = None

        # 候选点排序：利用 evaluator 的快速评估提升剪枝效率
        candidates = self._get_candidates()
        candidates.sort(key=lambda m: self.evaluator.quick_point_score(m[0], m[1], self.player_id), reverse=True)

        for x, y in candidates:
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutError

            self.engine.make_move(x, y, self.player_id)
            try:
                # 进入递归
                val = self.minimax(depth - 1, -float('inf'), float('inf'), False)
                if val > best_val:
                    best_val = val
                    best_pos = (x, y)
            finally:
                # 【鲁棒性核心】确保棋盘状态一定会回滚
                self.engine.undo_move(x, y)

        return best_pos, best_val

    def minimax(self, depth, alpha, beta, is_maximizing):
        """带 Alpha-Beta 剪枝的 Minimax 递归"""
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError

        # --- 置换表查询 ---
        board_hash = self.engine.current_hash
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                if entry['type'] == EXACT: return entry['score']
                if entry['type'] == LOWERBOUND: alpha = max(alpha, entry['score'])
                if entry['type'] == UPPERBOUND: beta = min(beta, entry['score'])
                if alpha >= beta: return entry['score']

        if depth == 0:
            return self.evaluator.evaluate_board(self.player_id)

        candidates = self._get_candidates()
        curr_id = self.player_id if is_maximizing else self.opponent_id

        # 每一层都进行快速排序，显著减少分支数
        candidates.sort(key=lambda m: self.evaluator.quick_point_score(m[0], m[1], curr_id), reverse=True)

        original_alpha = alpha
        best_score = -float('inf') if is_maximizing else float('inf')

        for x, y in candidates:
            self.engine.make_move(x, y, curr_id)
            try:
                score = self.minimax(depth - 1, alpha, beta, not is_maximizing)
                if is_maximizing:
                    best_score = max(best_score, score)
                    alpha = max(alpha, score)
                else:
                    best_score = min(best_score, score)
                    beta = min(beta, score)
            finally:
                # 【鲁棒性核心】确保递归嵌套中的每一层落子都能被正确撤销
                self.engine.undo_move(x, y)

            if beta <= alpha:
                break

        self._save_tt(board_hash, best_score, depth, original_alpha, beta)
        return best_score

    def _save_tt(self, h, s, d, a, b):
        """保存计算结果到置换表"""
        if s <= a:
            t = UPPERBOUND
        elif s >= b:
            t = LOWERBOUND
        else:
            t = EXACT
        self.transposition_table[h] = {'score': s, 'depth': d, 'type': t}

    def _get_candidates(self):
        """获取当前棋局周边 1 格内的有效落子点"""
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
        return list(candidates)