# Author: Hu Jia
# Date:

import numpy as np


# 分值表：反映了不同棋型的战略价值
SCORES = {
    'FIVE': 100000,      # 连五：游戏结束
    'ALIVE_FOUR': 10000,  # 活四：对手若不堵即死，我方若有即胜
    'DEAD_FOUR': 1000,    # 冲四：有一定威胁，但容易防守
    'ALIVE_THREE': 1000,  # 活三：非常强力，能衍生出活四
    'DEAD_THREE': 100,    # 死三：普通进攻
    'ALIVE_TWO': 100,     # 活二：基础潜力
    'DEAD_TWO': 10,       # 死二：微弱潜力
}

# 定义匹配模式 (1代表当前玩家，0代表空位)
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
        """
        评估整个棋盘对指定 player 的分数。
        总分 = 己方棋型分值 - 敌方棋型分值 * 1.2 (略微侧重防守)
        """
        opponent = 3 - player
        my_score = self.count_board_score(player)
        opp_score = self.count_board_score(opponent)
        return my_score - int(opp_score * 1.2)

    def count_board_score(self, player):
        score = 0
        lines = self._get_all_lines()
        player_char = str(player)
        opp_char = str(3 - player)

        for line in lines:
            # 将数字列表转为字符串，并根据当前玩家标准化
            # 把己方换成'1'，对方换成'2'，空位换成'0'
            line_str = "".join(map(str, line)).replace(player_char, '1').replace(opp_char, '2')
            score += self._score_line(line_str)
        return score

    def _score_line(self, line_str):
        line_score = 0
        for pattern_name, patterns in PATTERNS.items():
            for p in patterns:
                count = line_str.count(p)
                if count > 0:
                    line_score += count * SCORES[pattern_name]
        return line_score

    def _get_all_lines(self):
        """提取棋盘所有可能的行、列、对角线"""
        lines = []
        board = self.engine.board

        # 行
        for row in board:
            lines.append(row.tolist())
        # 列
        for col in board.T:
            lines.append(col.tolist())
        # 对角线 (右上到左下，左上到右下)
        for i in range(-self.size + 1, self.size):
            lines.append(board.diagonal(i).tolist())
            lines.append(np.fliplr(board).diagonal(i).tolist())

        # 只保留长度大于等于5的线
        return [l for l in lines if len(l) >= 5]