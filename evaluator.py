import numpy as np

# 分值层级：定义棋型的核心价值
SCORES = {
    'FIVE': 100000000,
    'ALIVE_FOUR': 10000000,
    'DEAD_FOUR': 1000000,
    'ALIVE_THREE': 100000,
    'DEAD_THREE': 10000,
    'ALIVE_TWO': 1000,
    'DEAD_TWO': 100,
}


class GomokuEvaluator:
    def __init__(self, engine):
        self.engine = engine
        self.size = engine.size

    def quick_point_score(self, x, y, player):
        """
        针对单个落子点的快速启发式评估（性能优化版）。
        直接统计周围棋子，不使用字符串操作，用于搜索过程中的节点排序。
        """
        score = 0
        opponent = 3 - player
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            my_count = 0
            opp_count = 0
            # 检查半径为 4 的局部区域
            for i in range(-4, 5):
                if i == 0: continue
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    cell = self.engine.board[nx][ny]
                    if cell == player:
                        my_count += 1
                    elif cell == opponent:
                        opp_count += 1

            # 启发式权重：进攻与防御的平衡
            score += my_count * 10
            score += int(opp_count * 11)  # 稍微偏向防守以增强鲁棒性

        # 基础位置分：鼓励 AI 向中心靠拢
        center = self.size // 2
        score += (center - abs(x - center)) + (center - abs(y - center))
        return score

    def evaluate_board(self, player):
        """全局评估函数：用于搜索树的叶子节点评分"""
        opponent = 3 - player
        my_score = self.count_board_score(player)
        opp_score = self.count_board_score(opponent)
        # 放大对手分数的权重（1.2倍）以强制 AI 关注威胁
        return int(my_score - opp_score * 1.2)

    def count_board_score(self, player):
        """扫描全图计算总分"""
        score = 0
        lines = self._get_all_lines()
        for line in lines:
            line_str = "".join(map(str, line))
            # 视角转换逻辑
            if player == 2:
                line_str = line_str.replace('1', 'X').replace('2', '1').replace('X', '2')
            score += self._score_line(line_str)
        score += self._get_position_bonus(player)
        return score

    def _score_line(self, line_str):
        """精细化的棋型模式匹配"""
        if '11111' in line_str: return SCORES['FIVE']
        line_score = 0
        if '011110' in line_str: line_score += SCORES['ALIVE_FOUR']
        # 冲四与跳冲四识别
        for p in ['11110', '01111', '10111', '11011', '11101']:
            if p in line_str:
                line_score += SCORES['DEAD_FOUR']
                break
        # 活三识别
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
                    bonus += (center - abs(x - center)) + (center - abs(y - center))
        return bonus

    def _get_all_lines(self):
        """获取所有可能的获胜线（横、竖、斜）"""
        lines = []
        board = self.engine.board
        for row in board: lines.append(row.tolist())
        for col in board.T: lines.append(col.tolist())
        for i in range(-self.size + 1, self.size):
            lines.append(board.diagonal(i).tolist())
            lines.append(np.fliplr(board).diagonal(i).tolist())
        return [l for l in lines if len(l) >= 5]