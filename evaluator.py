import numpy as np

# 分值层级：采用10倍差额，确保高阶棋型具有绝对统治力
SCORES = {
    'FIVE': 100000000,  # 连五：1亿
    'ALIVE_FOUR': 10000000,  # 活四：1000万
    'DEAD_FOUR': 1000000,  # 冲四：100万
    'ALIVE_THREE': 100000,  # 活三：10万
    'DEAD_THREE': 10000,  # 眠三：1万
    'ALIVE_TWO': 1000,  # 活二
    'DEAD_TWO': 100,  # 眠二
}


class GomokuEvaluator:
    def __init__(self, engine):
        self.engine = engine
        self.size = engine.size

    def evaluate_board(self, player):
        opponent = 3 - player
        # 计算攻防平衡：适当提高对手分数的权重（1.2倍），使AI更倾向于防守
        my_score = self.count_board_score(player)
        opp_score = self.count_board_score(opponent)

        # 核心：不再使用 if opp_score > XXX return 这种截断逻辑
        # 这样 AI 才能通过对比 my_score - opp_score 的差值，选出那个能让对方分数减小最多的点（即堵截点）
        return int(my_score - opp_score * 1.2)

    def count_board_score(self, player):
        score = 0
        lines = self._get_all_lines()

        for line in lines:
            line_str = "".join(map(str, line))
            # 统一视角：将当前评估者视为 '1'
            if player == 2:
                line_str = line_str.replace('1', 'X').replace('2', '1').replace('X', '2')

            score += self._score_line(line_str)

        # 加入微量的位置分（中心加分），作为棋型相同时的“破局”依据
        score += self._get_position_bonus(player)
        return score

    def _score_line(self, line_str):
        line_score = 0

        # 1. 连五判断
        if '11111' in line_str:
            return SCORES['FIVE']

        # 2. 活四 (011110)
        if '011110' in line_str:
            line_score += SCORES['ALIVE_FOUR']

        # 3. 冲四：精细化匹配所有变体 (11110, 01111, 10111, 11011, 11101)
        # 这解决了跳冲四不堵的问题
        for p in ['11110', '01111', '10111', '11011', '11101']:
            if p in line_str:
                line_score += SCORES['DEAD_FOUR']
                break  # 同一线段高阶优先

        # 4. 活三
        for p in ['01110', '011010', '010110']:
            if p in line_str:
                line_score += SCORES['ALIVE_THREE']
                break

        return line_score

    def _get_position_bonus(self, player):
        bonus = 0
        center = self.size // 2
        for x in range(self.size):
            for y in range(self.size):
                if self.engine.board[x][y] == player:
                    # 分值控制在个位数，不干扰大局评分
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