"""CommonPlayer - Human player"""

from model.entities.player import Player
from model.entities.ship import Ship


class CommonPlayer(Player):
    """Human player that interacts via interface"""

    def __init__(self, name="Player"):
        super().__init__(name)

    def place_ships(self):
        """
        Places the player's ships on the board.
        Simplified version with automatic placement.
        """
        default_ships = [
            ("Carrier", 5),
            ("Battleship", 4),
            ("Cruiser", 3),
            ("Submarine", 3),
            ("Destroyer", 2),
        ]

        # Fixed positioning to simplify
        positions = [
            (0, 0, True),  # Carrier: horizontal row 0
            (2, 0, True),  # Battleship: horizontal row 2
            (4, 0, True),  # Cruiser: horizontal row 4
            (6, 0, True),  # Submarine: horizontal row 6
            (8, 0, True),  # Destroyer: horizontal row 8
        ]

        for (name, size), (row, col, horizontal) in zip(default_ships, positions):
            ship = Ship(name, size)
            try:
                self.board.add_ship(ship, row, col, horizontal)
            except ValueError as e:
                print(f"Error placing {name}: {e}")

    def make_attack(self):
        """
        Human player doesn't make automatic attacks.
        Attack is made through the interface.
        """
        pass
