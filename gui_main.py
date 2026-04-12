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
        self.back_btn = pygame.Rect(SCREEN_SIZE - 360, SCREEN_SIZE + 20, 100, 40)
        # ⭐ 新增（放在按钮定义下面）
        self.settings_btn = pygame.Rect(SCREEN_SIZE - 360, SCREEN_SIZE + 20, 100, 40)

        # ⭐ 弹窗控制
        self.show_popup = False
        self.winner_text = ""

        # ⭐ 设置面板
        self.show_settings = False

        # ⭐ 难度
        self.difficulty = "medium"

        self.init_game()

    def init_game(self):
        self.engine = GomokuEngine(size=BOARD_SIZE)
        self.evaluator = GomokuEvaluator(self.engine)
        # ⭐ 替换这一行
        # self.ai = MinimaxAI(self.engine, self.evaluator, depth=3)

        if self.difficulty == "easy":
            depth = 2
        elif self.difficulty == "hard":
            depth = 4
        else:
            depth = 3

        self.ai = MinimaxAI(self.engine, self.evaluator, depth=depth)

        self.game_over = False
        self.move_history = []
        self.current_player = 1

        # 测试是否真的修改了难度
        # print("当前难度:", self.difficulty)
        # print("AI深度:", depth)

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
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.settings_btn)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.restart_btn)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.undo_btn)

        self.screen.blit(self.font.render("设置", True, TEXT_COLOR),
                         (self.settings_btn.x + 20, self.settings_btn.y + 8))
        self.screen.blit(self.font.render("重新开始", True, TEXT_COLOR),
                         (self.restart_btn.x + 5, self.restart_btn.y + 8))
        self.screen.blit(self.font.render("悔棋", True, TEXT_COLOR),
                         (self.undo_btn.x + 25, self.undo_btn.y + 8))

    def draw_popup(self):
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 弹窗卡片
        rect = pygame.Rect(150, 200, 300, 200)
        pygame.draw.rect(self.screen, (250, 240, 220), rect, border_radius=10)

        # 文本
        text = self.font.render(self.winner_text, True, (50, 50, 50))
        self.screen.blit(text, (rect.x + 60, rect.y + 50))

        # 下一局按钮
        self.next_btn = pygame.Rect(rect.x + 100, rect.y + 120, 100, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.next_btn)
        self.screen.blit(self.font.render("下一局", True, TEXT_COLOR),
                         (self.next_btn.x + 10, self.next_btn.y + 8))

    def draw_settings(self):
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        rect = pygame.Rect(150, 180, 300, 260)
        pygame.draw.rect(self.screen, (245, 235, 210), rect, border_radius=10)

        title = self.font.render("设置", True, TEXT_COLOR)
        self.screen.blit(title, (rect.x + 120, rect.y + 20))

        # 返回主页
        self.home_btn = pygame.Rect(rect.x + 80, rect.y + 70, 140, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.home_btn)
        self.screen.blit(self.font.render("返回主页", True, TEXT_COLOR),
                         (self.home_btn.x + 10, self.home_btn.y + 8))

        # ⭐ 返回游戏按钮
        self.back_game_btn = pygame.Rect(rect.x + 80, rect.y + 110, 140, 40)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.back_game_btn)
        self.screen.blit(self.font.render("返回游戏", True, TEXT_COLOR),
                         (self.back_game_btn.x + 10, self.back_game_btn.y + 8))

        # 难度按钮
        self.easy_btn = pygame.Rect(rect.x + 20, rect.y + 140, 80, 40)
        self.mid_btn = pygame.Rect(rect.x + 110, rect.y + 140, 80, 40)
        self.hard_btn = pygame.Rect(rect.x + 200, rect.y + 140, 80, 40)

        # ⭐ 根据当前难度决定颜色
        easy_color = BUTTON_HOVER if self.difficulty == "easy" else BUTTON_COLOR
        mid_color = BUTTON_HOVER if self.difficulty == "medium" else BUTTON_COLOR
        hard_color = BUTTON_HOVER if self.difficulty == "hard" else BUTTON_COLOR

        pygame.draw.rect(self.screen, easy_color, self.easy_btn)
        pygame.draw.rect(self.screen, mid_color, self.mid_btn)
        pygame.draw.rect(self.screen, hard_color, self.hard_btn)

        self.screen.blit(self.font.render("简单", True, TEXT_COLOR), (self.easy_btn.x + 10, self.easy_btn.y + 8))
        self.screen.blit(self.font.render("中等", True, TEXT_COLOR), (self.mid_btn.x + 10, self.mid_btn.y + 8))
        self.screen.blit(self.font.render("困难", True, TEXT_COLOR), (self.hard_btn.x + 10, self.hard_btn.y + 8))

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
                    self.winner_text = f"{self.player1_name} 获胜！"
                else:
                    self.score_p2 += 1
                    self.winner_text = f"{self.player2_name} 获胜！"

                self.show_popup = True

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
                self.winner_text = f"{self.player2_name} 获胜！"
                self.show_popup = True

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

                if self.show_popup:
                    self.draw_popup()

                if self.show_settings:
                    self.draw_settings()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.pvp_btn.collidepoint(event.pos):
                            self.mode = "pvp"
                            self.input_text = ""  # ⭐ 清空输入
                            self.state = "input"

                        elif self.pve_btn.collidepoint(event.pos):
                            self.mode = "pve"
                            self.input_text = ""  # ⭐ 清空输入
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
                        # ================== ⭐ 1. 胜利弹窗优先 ==================
                        if self.show_popup:
                            if self.next_btn.collidepoint(event.pos):
                                self.show_popup = False
                                self.init_game()
                            continue  # ⭐ 阻止后续点击

                        # ================== ⭐ 2. 设置面板优先 ==================
                        if self.show_settings:
                            if self.home_btn.collidepoint(event.pos):
                                self.state = "menu"
                                self.show_settings = False
                                self.score_p1 = 0
                                self.score_p2 = 0
                                self.init_game()

                            elif self.back_game_btn.collidepoint(event.pos):
                                self.show_settings = False

                            elif self.easy_btn.collidepoint(event.pos):
                                self.difficulty = "easy"
                                self.init_game()  # ⭐ 重新创建AI
                            elif self.mid_btn.collidepoint(event.pos):
                                self.difficulty = "medium"
                                self.init_game()
                            elif self.hard_btn.collidepoint(event.pos):
                                self.difficulty = "hard"
                                self.init_game()
                            continue  # ⭐ 阻止落子

                        # ================== ⭐ 3. 正常按钮 ==================
                        if self.settings_btn.collidepoint(event.pos):
                            self.show_settings = True
                            continue
                        if self.restart_btn.collidepoint(event.pos):
                            self.init_game()
                            continue
                        if self.undo_btn.collidepoint(event.pos):
                            if len(self.move_history) >= 2:
                                r, c = self.move_history.pop()
                                self.engine.undo_move(r, c)
                                r, c = self.move_history.pop()
                                self.engine.undo_move(r, c)
                            continue

                        # ================== ⭐ 4. 棋盘点击 ==================
                        if self.handle_click(event.pos):
                            self.draw_board()
                            self.draw_pieces()
                            self.draw_ui()
                            pygame.display.flip()
                            pygame.event.pump()
                            self.ai_turn()


if __name__ == "__main__":
    GomokuGUI().run()