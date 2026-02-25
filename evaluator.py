import numpy as np

# 关键：大幅拉开分值。让“活三”的分数远高于“死二”，迫使 AI 追求进攻。
SCORES = {
    'FIVE': 1000000,
    'ALIVE_FOUR': 100000,
    'DEAD_FOUR': 10000,
    'ALIVE_THREE': 8000,   # 进一步调高，确保它能压过位置分
    'DEAD_THREE': 1000,
    'ALIVE_TWO': 500,      # 活二适中
    'DEAD_TWO': 100,
}

PATTERNS = {
    'FIVE': ['11111'],
    'ALIVE_FOUR': ['011110'],
    'DEAD_FOUR': ['211110', '011112', '11101', '10111', '11011'],
    'ALIVE_THREE': ['01110', '011010', '010110'],
    'DEAD_THREE': ['001112', '211100', '010112', '211010', '210110', '011012', '11001', '10011', '10101'],
    'ALIVE_TWO': ['001100', '01010', '010010'],
    'DEAD_TWO': ['000112', '211000', '001012', '210100']
}


class GomokuEvaluator:
    def __init__(self, engine):
        self.engine = engine
        self.size = engine.size

    def evaluate_board(self, player):
        opponent = 3 - player
        my_score = self.count_board_score(player)
        opp_score = self.count_board_score(opponent)

        # 进攻权重 1.0，防守权重 0.8。只有当你快赢了，AI 才会拼命挡你。
        # 否则，它会优先发展自己的连子。
        return int(my_score - opp_score * 0.8)

    def count_board_score(self, player):
        score = 0
        lines = self._get_all_lines()
        player_char = str(player)
        opp_char = str(3 - player)

        for line in lines:
            # 关键修正：确保转换逻辑无误
            # 我们要把“当前分析的玩家”统一替换为 '1'，对手替换为 '2'
            line_str = "".join(map(str, line))

            # 如果 player 是 2 (白棋)，那么要把 2 换成 1，把 1 换成 2
            if player == 2:
                line_str = line_str.replace('2', 'T').replace('1', '2').replace('T', '1')
            # 如果 player 是 1 (黑棋)，保持不变（因为模式库里 1 就是己方）

            score += self._score_line(line_str)

        score += self._get_position_bonus(player)
        return score

    def _score_line(self, line_str):
        line_score = 0
        for pattern_name, patterns in PATTERNS.items():
            for p in patterns:
                count = line_str.count(p)
                line_score += count * SCORES[pattern_name]
        return line_score

    def _get_position_bonus(self, player):
        bonus = 0
        center = self.size // 2
        for x in range(self.size):
            for y in range(self.size):
                if self.engine.board[x][y] == player:
                    # 距离中心越近，加分越多
                    bonus += (center - abs(x - center)) + (center - abs(y - center))
        return bonus

    def _get_all_lines(self):
        lines = []
        board = self.engine.board
        for row in board: lines.append(row.tolist())
        for col in board.T: lines.append(col.tolist())
        for i in range(-self.size + 1, self.size):
            lines.append(board.diagonal(i).tolist())
            lines.append(np.fliplr(board).diagonal(i).tolist())
        return [l for l in lines if len(l) >= 5]