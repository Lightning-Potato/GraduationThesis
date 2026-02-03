# Author: Hu Jia
# Date:

from gomoku_engine import GomokuEngine
from evaluator import GomokuEvaluator
from minimax_ai import MinimaxAI

def main():
    game = GomokuEngine()
    evaluator = GomokuEvaluator(game)
    # 初始化搜索深度为 2（深度每增加 1，计算量呈指数增长）
    ai = MinimaxAI(game, evaluator, depth=2)

    current_player = 1  # 玩家 1（黑棋）先手

    while True:
        print(game.board)
        if current_player == 1:
            move = input(f"玩家 {current_player} 落子 (x,y): ")
            x, y = map(int, move.split(','))
        else:
            print("AI 正在思考...")
            x, y = ai.get_best_move(current_player)
            print(f"AI 落子于: {x},{y}")

        if game.make_move(x, y, current_player):
            if game.check_win(x, y, current_player):
                print(game.board)
                print(f"获胜者是: {'玩家' if current_player == 1 else 'AI'}")
                break
            current_player = 3 - current_player
        else:
            print("无效落子！")


if __name__ == "__main__":
    main()