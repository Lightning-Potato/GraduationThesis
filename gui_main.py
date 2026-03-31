# Author: Hu Jia
# Date:

import pygame
import sys
from gomoku_engine import GomokuEngine
from minimax_ai import MinimaxAI
from evaluator import GomokuEvaluator

# ================== 配置参数 ==================
BOARD_SIZE = 15
GRID_SIZE = 40
MARGIN = 40
BOTTOM_PANEL = 80
SCREEN_SIZE = GRID_SIZE * (BOARD_SIZE - 1) + MARGIN * 2
WINDOW_HEIGHT = SCREEN_SIZE + BOTTOM_PANEL

BOARD_COLOR = (235, 185, 120)
BLACK = (30, 30, 30)
WHITE = (245, 245, 245)
TEXT_COLOR = (20, 20, 20)
BUTTON_COLOR = (200, 160, 100)
BUTTON_HOVER = (220, 180, 120)


class GomokuGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, WINDOW_HEIGHT))
        pygame.display.set_caption("毕业设计：五子棋 AI 对战演示")

        self.font = pygame.font.SysFont("simhei", 22)

        # 按钮区域
        self.restart_btn = pygame.Rect(SCREEN_SIZE - 240, SCREEN_SIZE + 20, 100, 40)
        self.undo_btn = pygame.Rect(SCREEN_SIZE - 120, SCREEN_SIZE + 20, 100, 40)

        self.init_game()

    # ================== 初始化游戏 ==================
    def init_game(self):
        self.engine = GomokuEngine(size=BOARD_SIZE)
        self.evaluator = GomokuEvaluator(self.engine)
        self.ai = MinimaxAI(self.engine, self.evaluator, depth=3)

        self.game_over = False
        self.status_text = "你的回合（黑棋）"
        self.move_history = []

        # ⭐ 新增：回合控制 + AI锁
        self.current_player = 1  # 1=玩家, 2=AI
        self.ai_thinking = False

    # ================== 重新对局 ==================
    def restart_game(self):
        self.init_game()

    # ================== 悔棋 ==================
    def undo_move(self):
        if len(self.move_history) >= 2:
            # 用 undo_move 保证哈希正确
            r, c = self.move_history.pop()
            self.engine.undo_move(r, c)

            r, c = self.move_history.pop()
            self.engine.undo_move(r, c)

            self.game_over = False
            self.current_player = 1
            self.status_text = "已悔棋，你的回合（黑棋）"

    # ================== 画棋盘 ==================
    def draw_board(self):
        self.screen.fill(BOARD_COLOR)

        for i in range(BOARD_SIZE):
            pygame.draw.line(self.screen, BLACK,
                             (MARGIN, MARGIN + i * GRID_SIZE),
                             (SCREEN_SIZE - MARGIN, MARGIN + i * GRID_SIZE), 1)

            pygame.draw.line(self.screen, BLACK,
                             (MARGIN + i * GRID_SIZE, MARGIN),
                             (MARGIN + i * GRID_SIZE, SCREEN_SIZE - MARGIN), 1)

        for pts in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
            pygame.draw.circle(self.screen, BLACK,
                               (MARGIN + pts[0] * GRID_SIZE,
                                MARGIN + pts[1] * GRID_SIZE), 4)

    # ================== 画棋子 ==================
    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.engine.board[r][c]
                if piece != 0:
                    color = BLACK if piece == 1 else WHITE
                    pos = (MARGIN + c * GRID_SIZE,
                           MARGIN + r * GRID_SIZE)
                    pygame.draw.circle(
                        self.screen, color, pos,
                        GRID_SIZE // 2 - 2
                    )

    # ================== 画按钮 ==================
    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()

        for rect, text in [(self.restart_btn, "重新开始"),
                           (self.undo_btn, "悔棋")]:

            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)

            text_surface = self.font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

    # ================== 状态栏 ==================
    def draw_status(self):
        panel_rect = pygame.Rect(0, SCREEN_SIZE, SCREEN_SIZE, BOTTOM_PANEL)
        pygame.draw.rect(self.screen, (210, 170, 110), panel_rect)

        text_surface = self.font.render(self.status_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (20, SCREEN_SIZE + 25))

    # ================== 玩家落子 ==================
    def handle_click(self, pos):
        # ⭐ 关键限制（防止AI期间操作）
        if self.game_over or self.current_player != 1 or self.ai_thinking:
            return False

        x, y = pos
        if y > SCREEN_SIZE:
            return False

        col = round((x - MARGIN) / GRID_SIZE)
        row = round((y - MARGIN) / GRID_SIZE)

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.engine.make_move(row, col, 1):
                self.move_history.append((row, col))

                if self.engine.check_win(row, col, 1):
                    self.status_text = "恭喜你赢了！"
                    self.game_over = True
                else:
                    self.status_text = "AI 正在思考..."
                    self.current_player = 2  # ⭐ 切换到AI
                return True
        return False

    # ================== AI回合 ==================
    def ai_turn(self):
        # ⭐ 防止重复调用
        if self.game_over or self.current_player != 2 or self.ai_thinking:
            return

        self.ai_thinking = True

        move = self.ai.get_best_move(2)
        if move:
            r, c = move
            self.engine.make_move(r, c, 2)
            self.move_history.append((r, c))

            if self.engine.check_win(r, c, 2):
                self.status_text = "AI 赢了！"
                self.game_over = True
            else:
                self.status_text = "你的回合（黑棋）"
                self.current_player = 1  # ⭐ 切回玩家

        self.ai_thinking = False

    # ================== 主循环 ==================
    def run(self):
        while True:
            self.draw_board()
            self.draw_pieces()
            self.draw_status()
            self.draw_buttons()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos

                    if self.restart_btn.collidepoint(mouse_pos):
                        self.restart_game()

                    elif self.undo_btn.collidepoint(mouse_pos):
                        self.undo_move()

                    elif self.handle_click(mouse_pos):
                        self.draw_board()
                        self.draw_pieces()
                        self.draw_status()
                        self.draw_buttons()
                        pygame.display.flip()

                        # ⭐ 只在正确状态触发AI
                        if self.current_player == 2:
                            self.ai_turn()


if __name__ == "__main__":
    gui = GomokuGUI()
    gui.run()