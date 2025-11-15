"""Classe Board - representa o tabuleiro de batalha naval"""


class Board:
    """Tabuleiro de batalha naval com grid de células"""

    def __init__(self, size=10):
        self.size = size
        self.grid = [["~" for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.attacks = set()  # Already attacked positions
        self.hits = set()  # Positions that hit ships

    def add_ship(self, ship, start_row, start_col, horizontal=True):
        """Adds a ship to the board"""
        positions = []

        # Calculate ship positions
        for i in range(ship.size):
            if horizontal:
                row, col = start_row, start_col + i
            else:
                row, col = start_row + i, start_col

            # Check boundaries
            if row >= self.size or col >= self.size:
                raise ValueError("Ship outside board boundaries")

            # Check collision
            if self.grid[row][col] != "~":
                raise ValueError("Position already occupied by another ship")

            positions.append((row, col))

        # Place the ship
        ship.place(positions)
        for row, col in positions:
            self.grid[row][col] = "N"  # N = ship

        self.ships.append(ship)

    def receive_attack(self, row, col):
        """
        Processes an attack at a position.
        Returns: ('water', None) or ('hit', ship) or ('already_attacked', None)
        """
        position = (row, col)

        # Check if already attacked
        if position in self.attacks:
            return ("already_attacked", None)

        self.attacks.add(position)

        # Check if hit any ship
        for ship in self.ships:
            if ship.receive_attack(position):
                self.hits.add(position)
                self.grid[row][col] = "X"  # X = hit
                return ("hit", ship)

        # Water
        self.grid[row][col] = "O"  # O = water/miss
        return ("water", None)

    def all_ships_destroyed(self):
        """Checks if all ships were destroyed"""
        return all(ship.is_destroyed() for ship in self.ships)

    def show(self, hide_ships=False):
        """Returns visual representation of the board"""
        lines = []
        # Header with column numbers
        lines.append("   " + " ".join(str(i) for i in range(self.size)))
        lines.append("  " + "-" * (self.size * 2 + 1))

        for i, row in enumerate(self.grid):
            cells = []
            for j, cell in enumerate(row):
                if hide_ships and cell == "N":
                    cells.append("~")
                else:
                    cells.append(cell)
            lines.append(f"{i} | " + " ".join(cells))

        return "\n".join(lines)
