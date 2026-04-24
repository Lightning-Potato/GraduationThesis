import time
import numpy as np
import config

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class MinimaxAI:
    def __init__(self, engine, evaluator, depth=config.AI_CONFIG['MAX_DEPTH'],):
        self.engine = engine
        self.evaluator = evaluator
        self.max_depth = depth
        self.transposition_table = {}
        self.time_limit = config.AI_CONFIG['TIME_LIMIT']  # Maximum thinking time limit
        self.start_time = 0

        '记录相关指标'
        self.nodes_visited = 0  # Total number of nodes accessed
        self.tt_hits = 0  # Number of times the permutation table is hit
        self.cutoffs = 0  # Number of pruning events
        self.search_history = []  # Detailed data used to record each step

    def get_best_move(self, player_id):
        self.player_id = player_id
        self.opponent_id = 3 - player_id

        # --- Optimization: Opening Strategy ---
        # If the board is completely empty, play directly in the center position to avoid wasting computing power.
        if np.sum(self.engine.board != 0) == 0:
            return (self.engine.size // 2, self.engine.size // 2)

        self.start_time = time.time()

        # Regularly clean up the replacement table to prevent memory overflow
        if len(self.transposition_table) > config.AI_CONFIG['TT_SIZE_LIMIT']:
            self.transposition_table.clear()

        best_move = None
        last_completed_depth = 0

        # --- Core Logic: Iterative Deepening of the Search ---
        for current_depth in range(1, self.max_depth + 1):
            try:
                move, score = self._search_at_depth(current_depth)
                if move:
                    best_move = move
                    last_completed_depth = current_depth

                # Winning Pruning: Stop deepening the search once a winning path is found.
                if score >= config.BOARD_SCORES['ALIVE_FOUR']: break

                # Time Warning: If 80% of the time has been consumed, the next depth level will not be opened.
                if time.time() - self.start_time > self.time_limit * 0.8: break
            except TimeoutError:
                break

        print(f"\n--- AI is thinking ---")
        print(f"Position: {best_move} | Depth: {last_completed_depth} | Time: {time.time() - self.start_time:.2f}s")
        return best_move

    def _search_at_depth(self, depth):
        """Root Node Search Logic"""
        best_val = -float('inf')
        best_pos = None

        # Candidate Ranking: Improving Pruning Efficiency Through Rapid Evaluation by Evaluator
        candidates = self._get_candidates()
        candidates.sort(key=lambda m: self.evaluator.quick_point_score(m[0], m[1], self.player_id), reverse=True)

        for x, y in candidates:
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutError

            self.engine.make_move(x, y, self.player_id)
            try:
                # Entering recursion
                val = self.minimax(depth - 1, -float('inf'), float('inf'), False)
                if val > best_val:
                    best_val = val
                    best_pos = (x, y)
            finally:
                # [Robust Core] Ensures the board state will always be rolled back.
                self.engine.undo_move(x, y)

        return best_pos, best_val

    def minimax(self, depth, alpha, beta, is_maximizing):

        self.nodes_visited += 1  # Each time the recursion is entered, the count is incremented by 1.

        """Minimax Recursion with Alpha-Beta Pruning"""
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError

        # --- Replacement table lookup ---
        board_hash = self.engine.current_hash
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:

                self.tt_hits += 1  # Hit Count

                if entry['type'] == EXACT: return entry['score']
                if entry['type'] == LOWERBOUND: alpha = max(alpha, entry['score'])
                if entry['type'] == UPPERBOUND: beta = min(beta, entry['score'])
                if alpha >= beta: return entry['score']

        if depth == 0:
            return self.evaluator.evaluate_board(self.player_id)

        candidates = self._get_candidates()
        curr_id = self.player_id if is_maximizing else self.opponent_id

        # Perform quicksort at each level to significantly reduce the number of branches.
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
                # [Robust Core] Ensure that every move in a nested recursion can be correctly undone.
                self.engine.undo_move(x, y)

            if beta <= alpha:

                self.cutoffs += 1  # 计数剪枝

                break

        self._save_tt(board_hash, best_score, depth, original_alpha, beta)
        return best_score

    def _save_tt(self, h, s, d, a, b):
        """Save the calculation results to the permutation table."""
        if s <= a:
            t = UPPERBOUND
        elif s >= b:
            t = LOWERBOUND
        else:
            t = EXACT
        self.transposition_table[h] = {'score': s, 'depth': d, 'type': t}

    def _get_candidates(self):
        """Get the valid placement points within 1 square around the current chessboard."""
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