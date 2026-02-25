# Author: Hu Jia
# Date:

import pygame
import sys
# 导入你之前的逻辑文件
from gomoku_engine import GomokuEngine
from minimax_ai import MinimaxAI
from evaluator import GomokuEvaluator

# 配置参数
BOARD_SIZE = 15
GRID_SIZE = 40  # 每个格子的像素大小
MARGIN = 40  # 棋盘边缘留白
SCREEN_SIZE = GRID_SIZE * (BOARD_SIZE - 1) + MARGIN * 2

# 颜色定义
BOARD_COLOR = (235, 185, 120)  # 经典木质棋盘色
BLACK = (30, 30, 30)
WHITE = (245, 245, 245)


class GomokuGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("毕业设计：五子棋 AI 对战演示")

        # 初始化后端逻辑
        self.engine = GomokuEngine(size=BOARD_SIZE)
        self.evaluator = GomokuEvaluator(self.engine)
        self.ai = MinimaxAI(self.engine, self.evaluator, depth=3)  # 先用3层测试

        self.game_over = False

    def draw_board(self):
        self.screen.fill(BOARD_COLOR)
        # 画直线
        for i in range(BOARD_SIZE):
            # 横线
            pygame.draw.line(self.screen, BLACK,
                             (MARGIN, MARGIN + i * GRID_SIZE),
                             (SCREEN_SIZE - MARGIN, MARGIN + i * GRID_SIZE), 1)
            # 竖线
            pygame.draw.line(self.screen, BLACK,
                             (MARGIN + i * GRID_SIZE, MARGIN),
                             (MARGIN + i * GRID_SIZE, SCREEN_SIZE - MARGIN), 1)

        # 画天元和星位 (15x15 棋盘的常用参考点)
        for pts in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
            pygame.draw.circle(self.screen, BLACK,
                               (MARGIN + pts[0] * GRID_SIZE, MARGIN + pts[1] * GRID_SIZE), 4)

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.engine.board[r][c]
                if piece != 0:
                    color = BLACK if piece == 1 else WHITE
                    pos = (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE)
                    pygame.draw.circle(self.screen, color, pos, GRID_SIZE // 2 - 2)

    def handle_click(self, pos):
        if self.game_over: return

        # 将像素坐标转为棋盘索引
        x, y = pos
        col = round((x - MARGIN) / GRID_SIZE)
        row = round((y - MARGIN) / GRID_SIZE)

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.engine.make_move(row, col, 1):  # 玩家是 1 (黑棋)
                if self.engine.check_win(row, col, 1):
                    print("恭喜！你赢了！")
                    self.game_over = True
                return True
        return False

    def ai_turn(self):
        if self.game_over: return
        print("AI 正在思考...")
        # 刷新界面显示“AI正在思考”的状态
        pygame.display.set_caption("AI 正在思考中...")

        move = self.ai.get_best_move(2)  # AI 是 2 (白棋)
        if move:
            r, c = move
            self.engine.make_move(r, c, 2)
            if self.engine.check_win(r, c, 2):
                print("AI 赢了！再接再厉。")
                self.game_over = True

        pygame.display.set_caption("毕业设计：五子棋 AI 对战演示")

    def run(self):
        while True:
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if self.handle_click(event.pos):
                        # 玩家下完后立即刷新棋盘，再让 AI 走
                        self.draw_board()
                        self.draw_pieces()
                        pygame.display.flip()

                        self.ai_turn()


if __name__ == "__main__":
    gui = GomokuGUI()
    gui.run()