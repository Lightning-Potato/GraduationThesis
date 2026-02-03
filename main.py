# Author: Hu Jia
# Date:

from gomoku_engine import GomokuEngine
from greedy_ai import GreedyAI

def main():
    game = GomokuEngine()
    ai = GreedyAI(game, player_id=2)  # AI 执白棋
    current_player = 1  # 玩家 1（黑棋）先手

    while True:
        print(game.board)
        if current_player == 1:
            move = input(f"玩家 {current_player} 落子 (x,y): ")
            x, y = map(int, move.split(','))
        else:
            print("AI 正在思考...")
            x, y = ai.get_best_move()
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