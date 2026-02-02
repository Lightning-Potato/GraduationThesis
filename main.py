# Author: Hu Jia
# Date:

from gomoku_engine import GomokuEngine


def main():
    game = GomokuEngine()
    current_player = 1  # 1 为黑棋先手

    print("--- 五子棋核心引擎测试 ---")
    while True:
        print(game.board)
        try:
            move = input(f"玩家 {current_player} 落子 (输入 x,y): ")
            x, y = map(int, move.split(','))

            if game.make_move(x, y, current_player):
                if game.check_win(x, y, current_player):
                    print(game.board)
                    print(f"恭喜！玩家 {current_player} 获胜！")
                    break
                current_player = 2 if current_player == 1 else 1
            else:
                print("无效落子，请重试。")
        except ValueError:
            print("输入格式错误，请输入 x,y (如 7,7)")


if __name__ == "__main__":
    main()