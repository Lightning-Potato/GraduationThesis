# Author: Hu Jia
# Date:

import numpy as np


class GomokuEngine:
    def __init__(self, size=15):
        self.size = size
        # 0: Empty, 1: Black (first move), 2: White
        self.board = np.zeros((size, size), dtype=int)
        self.last_move = None

        # --- Zobrist Hashing Initialization ---
        # Generate a random 64-bit integer for each state (3 possibilities: empty, black, white) of each cell (size*size) on the chessboard.
        # np.uint64 ensures a sufficiently large hash value range to reduce hash collisions.
        self.zobrist_table = np.random.randint(0, 2 ** 63, size=(size, size, 3), dtype=np.uint64)
        # Initialize the hash value of the current chessboard
        self.current_hash = self._calculate_full_hash()

    def _calculate_full_hash(self):
        """Calculate the complete hash value of the initial state (completely empty)"""
        h = np.uint64(0)
        for x in range(self.size):
            for y in range(self.size):
                # Initially, each cell is 0 (empty).
                h ^= self.zobrist_table[x][y][0]
        return h

    def is_valid_move(self, x, y):
        "Check if the coordinates are within the chessboard and are empty."
        return 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == 0

    def make_move(self, x, y, player):
        """Place the piece and update the Zobrist hash value simultaneously."""
        if self.is_valid_move(x, y):
            # 1. Remove the "empty" state at that position in the hash value using XOR.
            self.current_hash ^= self.zobrist_table[x][y][0]

            # 2. Update the chessboard array
            self.board[x][y] = player
            self.last_move = (x, y)

            # 3. Add the new piece state at that position to the hash value using an XOR operation.
            self.current_hash ^= self.zobrist_table[x][y][player]
            return True
        return False

    def undo_move(self, x, y):
        """Rollback Move (Extremely Important for AI Search):Return the piece to an empty space and update the hash value simultaneously."""
        player = self.board[x][y]
        if player != 0:
            # 1. Remove piece status
            self.current_hash ^= self.zobrist_table[x][y][player]
            # 2. Restore empty state
            self.board[x][y] = 0
            self.current_hash ^= self.zobrist_table[x][y][0]
            self.last_move = None  # Note: For simplicity, last_move will no longer be recorded after undo.

    def check_win(self, x, y, player):
        "Check if the current placement position achieves a five-in-a-row."
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            # Positive Exploration
            tx, ty = x + dx, y + dy
            while 0 <= tx < self.size and 0 <= ty < self.size and self.board[tx][ty] == player:
                count += 1
                tx += dx
                ty += dy
            # Reverse Exploration
            tx, ty = x - dx, y - dy
            while 0 <= tx < self.size and 0 <= ty < self.size and self.board[tx][ty] == player:
                count += 1
                tx -= dx
                ty -= dy
            if count >= 5:
                return True
        return False

    def reset(self):
        "Reset the chessboard and reinitialize the hashes"
        self.board.fill(0)
        self.last_move = None
        self.current_hash = self._calculate_full_hash()