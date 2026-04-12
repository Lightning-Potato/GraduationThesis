# Author: Hu Jia

import pygame
import sys
from gomoku_engine import GomokuEngine
from minimax_ai import MinimaxAI
from evaluator import GomokuEvaluator
import config

# ================== 配置 ==================
BOARD_SIZE = config.BOARD_SIZE
GRID_SIZE = config.GRID_SIZE
MARGIN = config.MARGIN
BOTTOM_PANEL = config.BOTTOM_PANEL
SCREEN_SIZE = config.SCREEN_SIZE
WINDOW_HEIGHT = config.WINDOW_HEIGHT

BOARD_COLOR = config.COLORS['BACKGROUND']
BLACK = config.COLORS['BLACK']
WHITE = config.COLORS['WHITE']
TEXT_COLOR = config.COLORS['TEXT_COLOR']
BUTTON_COLOR = config.COLORS['BUTTON_COLOR']
BUTTON_HOVER = config.COLORS['BUTTON_HOVER']


class GomokuGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, WINDOW_HEIGHT))
        pygame.display.set_caption("五子棋 AI")

        self.font = pygame.font.SysFont("simhei", 22)

        # 状态机
        self.state = "menu"  # menu / input / game
        self.mode = None     # "pvp" or "pve"

        self.player1_name = ""
        self.player2_name = ""
        self.input_text = ""

        # 计分
        self.score_p1 = 0
        self.score_p2 = 0

        # 按钮
        self.pvp_btn = pygame.Rect(200, 200, 200, 60)
        self.pve_btn = pygame.Rect(200, 300, 200, 60)

        self.restart_btn = pygame.Rect(SCREEN_SIZE - 240, SCREEN_SIZE + 20, 100, 40)
        self.undo_btn = pygame.Rect(SCREEN_SIZE - 120, SCREEN_SIZE + 20, 100, 40)

        self.init_game()

    def init_game(self):
        self.engine = GomokuEngine(size=BOARD_SIZE)
        self.evaluator = GomokuEvaluator(self.engine)
        self.ai = MinimaxAI(self.engine, self.evaluator, depth=3)

        self.game_over = False
        self.move_history = []
        self.current_player = 1

    # ================== 菜单 ==================
    def draw_menu(self):
        self.screen.fill(BOARD_COLOR)

        title = self.font.render("选择模式", True, TEXT_COLOR)
        self.screen.blit(title, (260, 120))

        pygame.draw.rect(self.screen, BUTTON_COLOR, self.pvp_btn)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.pve_btn)

        self.screen.blit(self.font.render("人人对战", True, TEXT_COLOR), (250, 215))
        self.screen.blit(self.font.render("人机对战", True, TEXT_COLOR), (250, 315))

    # ================== 输入 ==================
    def draw_input(self):
        self.screen.fill(BOARD_COLOR)

        if self.mode == "pve":
            prompt = "输入玩家名字:"
        else:
            prompt = "输入玩家1,玩家2 (用逗号分隔):"

        self.screen.blit(self.font.render(prompt, True, TEXT_COLOR), (100, 200))
        self.screen.blit(self.font.render(self.input_text, True, TEXT_COLOR), (100, 250))

    # ================== 棋盘 ==================
    def draw_board(self):
        self.screen.fill(BOARD_COLOR)

        for i in range(BOARD_SIZE):
            pygame.draw.line(self.screen, BLACK,
                             (MARGIN, MARGIN + i * GRID_SIZE),
                             (SCREEN_SIZE - MARGIN, MARGIN + i * GRID_SIZE), 1)

            pygame.draw.line(self.screen, BLACK,
                             (MARGIN + i * GRID_SIZE, MARGIN),
                             (MARGIN + i * GRID_SIZE, SCREEN_SIZE - MARGIN), 1)

        # ⭐ 你的原始星位（完全保留）
        for pts in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
            pygame.draw.circle(self.screen, BLACK,
                               (MARGIN + pts[0] * GRID_SIZE,
                                MARGIN + pts[1] * GRID_SIZE), 4)

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.engine.board[r][c]
                if piece != 0:
                    color = BLACK if piece == 1 else WHITE
                    pygame.draw.circle(self.screen, color,
                                       (MARGIN + c * GRID_SIZE,
                                        MARGIN + r * GRID_SIZE),
                                       GRID_SIZE // 2 - 2)

    # ================== UI ==================
    def draw_ui(self):
        panel = pygame.Rect(0, SCREEN_SIZE, SCREEN_SIZE, BOTTOM_PANEL)
        pygame.draw.rect(self.screen, (210, 170, 110), panel)

        # 比分
        score_text = f"{self.player1_name} {self.score_p1} : {self.score_p2} {self.player2_name}"
        self.screen.blit(self.font.render(score_text, True, TEXT_COLOR), (20, SCREEN_SIZE + 10))

        # 按钮
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.restart_btn)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.undo_btn)

        self.screen.blit(self.font.render("重新开始", True, TEXT_COLOR),
                         (self.restart_btn.x + 5, self.restart_btn.y + 8))
        self.screen.blit(self.font.render("悔棋", True, TEXT_COLOR),
                         (self.undo_btn.x + 25, self.undo_btn.y + 8))

    # ================== 落子 ==================
    def handle_click(self, pos):
        if self.game_over:
            return False

        x, y = pos
        if y > SCREEN_SIZE:
            return False

        col = round((x - MARGIN) / GRID_SIZE)
        row = round((y - MARGIN) / GRID_SIZE)

        if self.engine.make_move(row, col, self.current_player):
            self.move_history.append((row, col))

            if self.engine.check_win(row, col, self.current_player):
                self.game_over = True

                if self.current_player == 1:
                    self.score_p1 += 1
                else:
                    self.score_p2 += 1

            self.current_player = 3 - self.current_player
            return True

        return False

    # ================== AI ==================
    def ai_turn(self):
        if self.mode != "pve" or self.current_player != 2 or self.game_over:
            return

        move = self.ai.get_best_move(2)
        if move:
            r, c = move
            self.engine.make_move(r, c, 2)
            self.move_history.append((r, c))

            if self.engine.check_win(r, c, 2):
                self.score_p2 += 1
                self.game_over = True

            self.current_player = 1

    # ================== 主循环 ==================
    def run(self):
        while True:
            if self.state == "menu":
                self.draw_menu()

            elif self.state == "input":
                self.draw_input()

            elif self.state == "game":
                self.draw_board()
                self.draw_pieces()
                self.draw_ui()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.pvp_btn.collidepoint(event.pos):
                            self.mode = "pvp"
                            self.state = "input"

                        elif self.pve_btn.collidepoint(event.pos):
                            self.mode = "pve"
                            self.state = "input"

                elif self.state == "input":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.mode == "pve":
                                self.player1_name = self.input_text
                                self.player2_name = "AI"
                            else:
                                names = self.input_text.split(",")
                                self.player1_name = names[0]
                                self.player2_name = names[1]

                            self.state = "game"
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode

                elif self.state == "game":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.restart_btn.collidepoint(event.pos):
                            self.init_game()

                        elif self.undo_btn.collidepoint(event.pos):
                            if len(self.move_history) >= 2:
                                r, c = self.move_history.pop()
                                self.engine.undo_move(r, c)
                                r, c = self.move_history.pop()
                                self.engine.undo_move(r, c)


                        elif self.handle_click(event.pos):
                            # ⭐ 先刷新，让玩家的棋子立刻显示
                            self.draw_board()
                            self.draw_pieces()
                            self.draw_ui()
                            pygame.display.flip()
                            pygame.event.pump()  # 防止窗口卡死
                            # ⭐ 再让 AI 思考
                            self.ai_turn()


if __name__ == "__main__":
    GomokuGUI().run()