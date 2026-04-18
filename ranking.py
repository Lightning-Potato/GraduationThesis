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

    def add_win(self, player_name):
        if player_name not in self.data:
            self.data[player_name] = 0
        self.data[player_name] += 1
        self.save()

    def get_ranking(self):
        # 按胜场排序
        return sorted(self.data.items(), key=lambda x: x[1], reverse=True)