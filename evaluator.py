import numpy as np
import config

# Scoring Tiers: Defining the Core Value of Chess Patterns
SCORES = config.BOARD_SCORES


class GomokuEvaluator:
    def __init__(self, engine):
        self.engine = engine
        self.size = engine.size

    def quick_point_score(self, x, y, player):
        """A fast heuristic evaluation for a single move (performance optimized).
        Directly counts surrounding pieces without string manipulation; used for node sorting during the search process.
        """
        score = 0
        opponent = 3 - player
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            my_count = 0
            opp_count = 0
            # Detection of a local area with a radius of 4
            for i in range(-4, 5):
                if i == 0: continue
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    cell = self.engine.board[nx][ny]
                    if cell == player:
                        my_count += 1
                    elif cell == opponent:
                        opp_count += 1

            # Heuristic Weighting: The Balance Between Offense and Defense
            score += my_count * 10
            score += int(opp_count * 11)  # Slightly biased towards defense to enhance robustness

        # Basic location score: Encourage AI to move closer to the center
        center = self.size // 2
        score += (center - abs(x - center)) + (center - abs(y - center))
        return score

    def evaluate_board(self, player):
        """Global evaluation function: used to score the leaf nodes of the search tree."""
        opponent = 3 - player
        my_score = self.count_board_score(player)
        opp_score = self.count_board_score(opponent)
        # Increase the weight of opponent scores (1.2x) to force AI to focus on threats.
        return int(my_score - opp_score * 1.2)

    def count_board_score(self, player):
        """Scan the entire image to calculate the total score"""
        score = 0
        lines = self._get_all_lines()
        for line in lines:
            line_str = "".join(map(str, line))
            # Perspective Shift Logic
            if player == 2:
                line_str = line_str.replace('1', 'X').replace('2', '1').replace('X', '2')
            score += self._score_line(line_str)
        score += self._get_position_bonus(player)
        return score

    def _score_line(self, line_str):
        """Refined chess pattern matching"""
        if '11111' in line_str: return SCORES['FIVE']
        line_score = 0
        if '011110' in line_str: line_score += SCORES['ALIVE_FOUR']
        # Identifying between a four-man rush and a jump four-man rush
        for p in ['11110', '01111', '10111', '11011', '11101']:
            if p in line_str:
                line_score += SCORES['DEAD_FOUR']
                break
        # Live Three Recognition
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
        """Get all possible winning lines (horizontal, vertical, diagonal)"""
        lines = []
        board = self.engine.board
        for row in board: lines.append(row.tolist())
        for col in board.T: lines.append(col.tolist())
        for i in range(-self.size + 1, self.size):
            lines.append(board.diagonal(i).tolist())
            lines.append(np.fliplr(board).diagonal(i).tolist())
        return [l for l in lines if len(l) >= 5]