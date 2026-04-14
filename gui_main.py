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

# ⭐ 黑白极简UI
UI_BG = (245, 245, 247)        # 页面背景（略灰白）
UI_PANEL = (255, 255, 255)     # 卡片白
UI_BORDER = (200, 200, 200)    # 细边框（很淡）
UI_HOVER = (235, 235, 235)     # hover
UI_TEXT = (20, 20, 20)         # 主文字

UI_SHADOW = (0, 0, 0, 30)      # 阴影（重点）
UI_ACCENT = (0, 0, 0)          # 主强调色（黑）
UI_PLACEHOLDER = (160, 160, 160)


class GomokuGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, WINDOW_HEIGHT))
        pygame.display.set_caption("Gomoku AI")

        self.font = pygame.font.SysFont("simhei", 22)

        self.state = "menu"
        self.mode = None
        self.rule_text = [
            "Gomoku Game Rules",
            "",
            "[Rules]",
            "Gomoku is played on a 15×15 board.",
            "Black moves first, and players take turns placing stones on empty intersections.",
            "The first player to form an unbroken line of five stones horizontally, vertically, or diagonally wins.",
        ]

        # 返回按钮
        self.rule_back_btn = pygame.Rect(220, 520, 160, 50)

        self.player1_name = ""
        self.player2_name = ""
        # self.input_text = ""

        self.score_p1 = 0
        self.score_p2 = 0

        # 按钮
        self.pvp_btn = pygame.Rect(200, 200, 200, 60)
        self.pve_btn = pygame.Rect(200, 300, 200, 60)
        self.rank_btn = pygame.Rect(200, 400, 200, 60)
        self.rule_btn = pygame.Rect(200, 500, 200, 60)

        self.restart_btn = pygame.Rect(SCREEN_SIZE - 240, SCREEN_SIZE + 20, 100, 40)
        self.undo_btn = pygame.Rect(SCREEN_SIZE - 120, SCREEN_SIZE + 20, 100, 40)
        self.settings_btn = pygame.Rect(SCREEN_SIZE - 360, SCREEN_SIZE + 20, 100, 40)

        # ⭐ 输入框
        self.input_box1 = pygame.Rect(180, 220, 260, 40)
        self.input_box2 = pygame.Rect(180, 300, 260, 40)
        self.confirm_btn = pygame.Rect(220, 380, 160, 50)

        self.input_active = 1  # 当前输入框（1 or 2）
        self.input_text1 = ""
        self.input_text2 = ""

        # 状态
        self.show_popup = False
        self.winner_text = ""
        self.show_settings = False
        self.difficulty = "medium"

        self.init_game()

    def init_game(self):
        self.engine = GomokuEngine(size=BOARD_SIZE)
        self.evaluator = GomokuEvaluator(self.engine)

        depth = {"easy": 2, "medium": 3, "hard": 4}[self.difficulty]
        self.ai = MinimaxAI(self.engine, self.evaluator, depth=depth)

        self.game_over = False
        self.move_history = []
        self.current_player = 1

    def draw_text_wrapped(self, text, x, y, max_width, line_height=28):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_surface = self.font.render(test_line, True, UI_TEXT)

            if text_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)

        for i, line in enumerate(lines):
            text_surface = self.font.render(line.strip(), True, UI_TEXT)
            self.screen.blit(text_surface, (x, y + i * line_height))

        return y + len(lines) * line_height

    # ================== UI组件 ==================
    def draw_button(self, rect, text):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)

        # ===== 阴影 =====
        shadow_rect = rect.move(0, 4)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=12)
        self.screen.blit(shadow_surf, shadow_rect)

        # ===== 按钮 =====
        color = UI_HOVER if hover else UI_PANEL
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, UI_BORDER, rect, 1, border_radius=12)

        # ===== ⭐ 自动缩放字体 =====
        font_size = 22
        font = pygame.font.SysFont("simhei", font_size)

        text_surface = font.render(text, True, UI_TEXT)

        # 如果太宽 → 缩小字体
        while text_surface.get_width() > rect.width - 20 and font_size > 12:
            font_size -= 1
            font = pygame.font.SysFont("simhei", font_size)
            text_surface = font.render(text, True, UI_TEXT)

        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_diff_btn(self, rect, text, selected):
        if selected:
            pygame.draw.rect(self.screen, UI_BORDER, rect)
            text_surface = self.font.render(text, True, UI_BG)
        else:
            pygame.draw.rect(self.screen, UI_BG, rect)
            pygame.draw.rect(self.screen, UI_BORDER, rect, 2)
            text_surface = self.font.render(text, True, UI_TEXT)

        self.screen.blit(text_surface, (rect.x + 10, rect.y + 8))

    # ================== 菜单 ==================
    def draw_menu(self):
        self.screen.fill(UI_BG)
        title_font = pygame.font.SysFont("simhei", 36)
        title_surface = title_font.render("Gomoku (Five in a Row) Battle", True, UI_TEXT)

        # ⭐ 关键：真正居中
        title_rect = title_surface.get_rect(center=(SCREEN_SIZE // 2, 120))

        self.screen.blit(title_surface, title_rect)

        self.draw_button(self.pve_btn, "Player vs. AI")
        self.draw_button(self.pvp_btn, "Player vs. Player")
        self.draw_button(self.rank_btn, "Rankings")
        self.draw_button(self.rule_btn, "Game Rules")

    def draw_rules(self):
        self.screen.fill(UI_BG)

        # ===== 标题 =====
        title_font = pygame.font.SysFont("simhei", 32)
        title = title_font.render("Game Rules", True, UI_TEXT)
        self.screen.blit(title, (240, 60))

        # ===== 卡片背景 =====
        rect = pygame.Rect(80, 120, SCREEN_SIZE - 160, 380)

        # 阴影
        shadow = rect.move(0, 6)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=16)
        self.screen.blit(shadow_surf, shadow)

        pygame.draw.rect(self.screen, UI_PANEL, rect, border_radius=16)

        # ===== 规则文本 =====
        y_offset = rect.y + 20
        max_width = rect.width - 40

        for line in self.rule_text:
            if line == "":
                y_offset += 15  # 空行间距
            else:
                y_offset = self.draw_text_wrapped(
                    line,
                    rect.x + 20,
                    y_offset,
                    max_width
                )

        # ===== 返回按钮 =====
        self.draw_button(self.rule_back_btn, "Back")

    # ================== 输入 ==================
    def draw_input(self):
        self.screen.fill(UI_BG)

        title = self.font.render("Enter player name", True, UI_TEXT)
        self.screen.blit(title, (220, 150))

        # ===== 玩家1 =====
        # ===== 输入框阴影 =====
        shadow = self.input_box1.move(0, 3)
        shadow_surf = pygame.Surface((self.input_box1.width, self.input_box1.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=10)
        self.screen.blit(shadow_surf, shadow)

        # ===== 输入框 =====
        border_color = UI_ACCENT if self.input_active == 1 else UI_BORDER
        pygame.draw.rect(self.screen, UI_PANEL, self.input_box1, border_radius=10)
        pygame.draw.rect(self.screen, border_color, self.input_box1, 2, border_radius=10)

        text1 = self.input_text1 if self.input_text1 else "Player1"
        color1 = UI_TEXT if self.input_text1 else UI_PLACEHOLDER
        self.screen.blit(self.font.render(text1, True, color1),
                         (self.input_box1.x + 10, self.input_box1.y + 8))

        # ===== 玩家2（仅PVP）=====
        if self.mode == "pvp":
            # ===== 输入框阴影 =====
            shadow = self.input_box2.move(0, 3)
            shadow_surf = pygame.Surface((self.input_box2.width, self.input_box2.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=10)
            self.screen.blit(shadow_surf, shadow)

            # ===== 输入框 =====
            border_color = UI_ACCENT if self.input_active == 1 else UI_BORDER
            pygame.draw.rect(self.screen, UI_PANEL, self.input_box2, border_radius=10)
            pygame.draw.rect(self.screen, border_color, self.input_box2, 2, border_radius=10)

            text2 = self.input_text2 if self.input_text2 else "Player2"
            color2 = UI_TEXT if self.input_text2 else UI_PLACEHOLDER
            self.screen.blit(self.font.render(text2, True, color2),
                             (self.input_box2.x + 10, self.input_box2.y + 8))

        # ===== 确认按钮 =====
        self.draw_button(self.confirm_btn, "Start Game")

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

        for pts in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
            pygame.draw.circle(self.screen, BLACK,
                               (MARGIN + pts[0] * GRID_SIZE,
                                MARGIN + pts[1] * GRID_SIZE), 4)

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.engine.board[r][c]
                if piece:
                    color = BLACK if piece == 1 else WHITE
                    pygame.draw.circle(self.screen, color,
                                       (MARGIN + c * GRID_SIZE,
                                        MARGIN + r * GRID_SIZE),
                                       GRID_SIZE // 2 - 2)

    # ================== UI ==================
    def draw_ui(self):
        panel = pygame.Rect(0, SCREEN_SIZE, SCREEN_SIZE, BOTTOM_PANEL)
        # 阴影
        shadow = panel.move(0, -3)
        shadow_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=12)
        self.screen.blit(shadow_surf, shadow)

        # 卡片
        pygame.draw.rect(self.screen, UI_PANEL, panel, border_radius=12)

        score = f"{self.player1_name} {self.score_p1} : {self.score_p2} {self.player2_name}"
        self.screen.blit(self.font.render(score, True, UI_TEXT), (20, SCREEN_SIZE + 10))

        self.draw_button(self.settings_btn, "Settings")
        self.draw_button(self.restart_btn, "Restart")
        self.draw_button(self.undo_btn, "Undo")

    # ================== 弹窗 ==================
    def draw_popup(self):
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        rect = pygame.Rect(150, 200, 300, 200)
        # 阴影
        shadow = rect.move(0, 6)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=16)
        self.screen.blit(shadow_surf, shadow)

        # 卡片
        pygame.draw.rect(self.screen, UI_PANEL, rect, border_radius=16)

        self.screen.blit(self.font.render(self.winner_text, True, UI_TEXT), (rect.x + 60, rect.y + 50))

        self.next_btn = pygame.Rect(rect.x + 100, rect.y + 120, 100, 40)
        self.draw_button(self.next_btn, "Next game")

    # ================== 设置 ==================
    def draw_settings(self):
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        rect = pygame.Rect(150, 180, 300, 260)
        pygame.draw.rect(self.screen, UI_BG, rect, border_radius=10)
        pygame.draw.rect(self.screen, UI_BORDER, rect, 2, border_radius=10)

        self.home_btn = pygame.Rect(rect.x + 80, rect.y + 70, 140, 40)
        self.back_game_btn = pygame.Rect(rect.x + 80, rect.y + 110, 140, 40)

        self.draw_button(self.home_btn, "Home")
        self.draw_button(self.back_game_btn, "Back")

        self.easy_btn = pygame.Rect(rect.x + 20, rect.y + 160, 80, 40)
        self.mid_btn = pygame.Rect(rect.x + 110, rect.y + 160, 80, 40)
        self.hard_btn = pygame.Rect(rect.x + 200, rect.y + 160, 80, 40)

        self.draw_diff_btn(self.easy_btn, "Easy", self.difficulty == "easy")
        self.draw_diff_btn(self.mid_btn, "Medium", self.difficulty == "medium")
        self.draw_diff_btn(self.hard_btn, "Hard", self.difficulty == "hard")

    # ================== 逻辑（不变） ==================
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
                    self.winner_text = f"{self.player1_name} Win！"
                else:
                    self.score_p2 += 1
                    self.winner_text = f"{self.player2_name} Win！"
                self.show_popup = True

            self.current_player = 3 - self.current_player
            return True
        return False

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
                self.winner_text = f"{self.player2_name} Win！"
                self.show_popup = True

            self.current_player = 1

    # ================== 主循环 ==================
    def run(self):
        while True:
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "input":
                self.draw_input()
            elif self.state == "rules":  # ⭐ 新增
                self.draw_rules()
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
                            self.input_text1 = ""
                            self.input_text2 = ""
                            self.input_active = 1
                            self.state = "input"
                        elif self.pve_btn.collidepoint(event.pos):
                            self.mode = "pve"
                            self.input_text1 = ""
                            self.input_text2 = ""
                            self.input_active = 1
                            self.state = "input"
                        elif self.rank_btn.collidepoint(event.pos):
                            print("排行榜（未实现）")
                        elif self.rule_btn.collidepoint(event.pos):
                            self.state = "rules"

                elif self.state == "rules":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.rule_back_btn.collidepoint(event.pos):
                            self.state = "menu"

                elif self.state == "input":
                    # ⭐ 鼠标点击（切换输入框 or 点击确认）
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.input_box1.collidepoint(event.pos):
                            self.input_active = 1
                        elif self.input_box2.collidepoint(event.pos):
                            self.input_active = 2
                        elif self.confirm_btn.collidepoint(event.pos):

                            # ===== 默认值处理 =====
                            if self.mode == "pve":
                                self.player1_name = self.input_text1 if self.input_text1 else "Player"
                                self.player2_name = "AI"
                            else:
                                self.player1_name = self.input_text1 if self.input_text1 else "Player1"
                                self.player2_name = self.input_text2 if self.input_text2 else "Player2"

                            self.state = "game"

                    # ⭐ 键盘输入
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            if self.input_active == 1:
                                self.input_text1 = self.input_text1[:-1]
                            else:
                                self.input_text2 = self.input_text2[:-1]
                        else:
                            if self.input_active == 1:
                                self.input_text1 += event.unicode
                            else:
                                self.input_text2 += event.unicode

                elif self.state == "game":
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        if self.show_popup:
                            if self.next_btn.collidepoint(event.pos):
                                self.show_popup = False
                                self.init_game()
                            continue

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
                                self.init_game()
                            elif self.mid_btn.collidepoint(event.pos):
                                self.difficulty = "medium"
                                self.init_game()
                            elif self.hard_btn.collidepoint(event.pos):
                                self.difficulty = "hard"
                                self.init_game()
                            continue

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

                        if self.handle_click(event.pos):
                            self.draw_board()
                            self.draw_pieces()
                            self.draw_ui()
                            pygame.display.flip()
                            pygame.event.pump()
                            self.ai_turn()


if __name__ == "__main__":
    GomokuGUI().run()