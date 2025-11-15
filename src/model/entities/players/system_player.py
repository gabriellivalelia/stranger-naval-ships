"""SystemPlayer - AI-controlled player (computer)"""

import random

from model.entities.player import Player
from model.entities.ship import Ship


class SystemPlayer(Player):
    """Computer-controlled player with simple AI"""

    def __init__(self, name="Computer"):
        super().__init__(name)
        self.attacked_positions = set()
        self.search_mode = False  # Active search mode after hit
        self.last_hit = None
        self.directions_to_test = []

    def place_ships(self):
        """Places ships randomly on the board"""
        default_ships = [
            ("Carrier", 5),
            ("Battleship", 4),
            ("Cruiser", 3),
            ("Submarine", 3),
            ("Destroyer", 2),
        ]

        for name, size in default_ships:
            ship = Ship(name, size)
            placed = False
            attempts = 0
            max_attempts = 100

            while not placed and attempts < max_attempts:
                row = random.randint(0, self.board.size - 1)
                col = random.randint(0, self.board.size - 1)
                horizontal = random.choice([True, False])

                try:
                    self.board.add_ship(ship, row, col, horizontal)
                    placed = True
                except ValueError:
                    attempts += 1

            if not placed:
                print(f"Warning: Could not place {name} after {max_attempts} attempts")

    def make_attack(self):
        """
        AI to choose the next attack position.
        Uses simple strategy: random attack until hit, then search around.
        """
        # If in search mode (hit a ship but didn't destroy it)
        if self.search_mode and self.last_hit:
            attack = self._smart_attack()
            if attack:
                return attack
            else:
                # If no more directions, return to random
                self.search_mode = False

        # Random attack
        return self._random_attack()

    def _random_attack(self):
        """Chooses a random position that hasn't been attacked yet"""
        size = self.board.size  # Use own board size (same as opponent's)
        available_positions = []

        for row in range(size):
            for col in range(size):
                if (row, col) not in self.attacked_positions:
                    available_positions.append((row, col))

        if available_positions:
            return random.choice(available_positions)
        return None

    def _smart_attack(self):
        """Attacks positions adjacent to the last hit"""
        if not self.last_hit:
            return None

        row, col = self.last_hit
        size = self.board.size  # Use own board size (same as opponent's)

        # Directions: up, down, left, right
        directions = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]

        # Filter valid and unattacked positions
        valid_positions = [
            (r, c)
            for r, c in directions
            if 0 <= r < size and 0 <= c < size and (r, c) not in self.attacked_positions
        ]

        if valid_positions:
            return random.choice(valid_positions)
        return None

    def record_attack_result(self, position, result, ship_destroyed):
        """Records attack result to improve next moves"""
        self.attacked_positions.add(position)

        if result == "hit":
            self.last_hit = position
            if not ship_destroyed:
                self.search_mode = True
            else:
                # Ship destroyed, return to random mode
                self.search_mode = False
                self.last_hit = None
