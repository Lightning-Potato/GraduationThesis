# Author: Hu Jia
# Date:

import json
import os

class RankingManager:
    def __init__(self, filename="rankings.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return {}
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def add_result(self, player_name, win=False):
        if player_name not in self.data:
            self.data[player_name] = {"win": 0, "games": 0}

        self.data[player_name]["games"] += 1
        if win:
            self.data[player_name]["win"] += 1

        self.trim_top_10()
        self.save()

    def get_ranking(self):
        ranking = []
        for name, stats in self.data.items():
            win = stats["win"]
            games = stats["games"]
            rate = win / games if games > 0 else 0
            ranking.append((name, win, games, rate))

        # ⭐ 按 胜场优先 + 胜率次之 排序
        ranking.sort(key=lambda x: (x[1], x[3]), reverse=True)
        return ranking

    def trim_top_10(self):
        ranking = self.get_ranking()
        top10 = ranking[:10]

        # 只保留前10
        new_data = {}
        for name, win, games, rate in top10:
            new_data[name] = {"win": win, "games": games}

        self.data = new_data