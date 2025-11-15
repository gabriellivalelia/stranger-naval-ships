"""Classe Ship - representa um navio no jogo de batalha naval"""


class Ship:
    """Representa um navio com posição, tamanho e estado"""

    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.positions = []  # List of tuples (row, col)
        self.hits = set()  # Positions that were hit

    def place(self, positions):
        """Places the ship at specified positions"""
        if len(positions) != self.size:
            raise ValueError(f"Ship {self.name} needs {self.size} positions")
        self.positions = positions

    def receive_attack(self, position):
        """Records an attack at a position. Returns True if hit"""
        if position in self.positions:
            self.hits.add(position)
            return True
        return False

    def is_destroyed(self):
        """Checks if the ship was completely destroyed"""
        return len(self.hits) == self.size

    def __repr__(self):
        return f"Ship({self.name}, size={self.size}, hits={len(self.hits)}/{self.size})"
