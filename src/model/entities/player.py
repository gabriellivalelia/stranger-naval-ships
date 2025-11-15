"""Player class - base class for players"""

from model.entities.board import Board


class Player:
    """Base class for players (human or computer)"""

    def __init__(self, name):
        self.name = name
        self.board = Board()

    def make_attack(self):
        """Abstract method - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement make_attack()")

    def place_ships(self):
        """Abstract method - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement place_ships()")

    def has_lost(self):
        """Checks if the player lost (all ships destroyed)"""
        return self.board.all_ships_destroyed()
