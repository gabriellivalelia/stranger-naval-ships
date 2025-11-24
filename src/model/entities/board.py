"""Classe Board - representa o tabuleiro de batalha naval"""


class Board:
    """Tabuleiro de batalha naval com grid de células"""

    def __init__(self, size=10):
        self._size = size
        self._grid = [["~" for _ in range(size)] for _ in range(size)]
        self._ships = []
        self._attacks = set()  # Posições já atacadas
        self._hits = set()  # Posições que acertaram navios

    # Propriedades de acesso
    @property
    def size(self):
        return self._size

    @property
    def grid(self):
        return self._grid

    @property
    def ships(self):
        return self._ships

    @property
    def attacks(self):
        return self._attacks

    @property
    def hits(self):
        return self._hits

    def add_ship(self, ship, start_row, start_col, horizontal=True):
        """Adiciona um navio ao tabuleiro"""
        positions = []

        # Calcula posições do navio
        for i in range(ship.size):
            if horizontal:
                row, col = start_row, start_col + i
            else:
                row, col = start_row + i, start_col

            # Verifica limites do tabuleiro
            if row >= self._size or col >= self._size:
                raise ValueError("Navio fora dos limites do tabuleiro")

            # Verifica colisão
            if self._grid[row][col] != "~":
                raise ValueError("Posição já ocupada por outro navio")

            positions.append((row, col))

        # Posiciona o navio
        ship.place(positions)
        for row, col in positions:
            self._grid[row][col] = "N"  # N = navio

        self._ships.append(ship)

    def receive_attack(self, row, col):
        """
        Processa um ataque em uma posição.
        Retorna: ('water', None) ou ('hit', ship) ou ('already_attacked', None)
        """
        position = (row, col)

        # Verifica se já foi atacado
        if position in self._attacks:
            return ("already_attacked", None)

        self._attacks.add(position)

        # Verifica se acertou algum navio
        for ship in self._ships:
            if ship.receive_attack(position):
                self._hits.add(position)
                self._grid[row][col] = "X"  # X = acerto
                return ("hit", ship)

        # Água
        self._grid[row][col] = "O"  # O = água/erro
        return ("water", None)

    def all_ships_destroyed(self):
        """Verifica se todos os navios foram destruídos"""
        result = all(ship.is_destroyed() for ship in self._ships)
        destroyed_count = sum(1 for ship in self._ships if ship.is_destroyed())
        print(
            f"[Board] all_ships_destroyed: {result} ({destroyed_count}/{len(self._ships)} navios destruídos)"
        )
        return result

    def show(self, hide_ships=False):
        """Retorna representação visual do tabuleiro"""
        lines = []
        # Cabeçalho com números das colunas
        lines.append("   " + " ".join(str(i) for i in range(self._size)))
        lines.append("  " + "-" * (self._size * 2 + 1))

        for i, row in enumerate(self._grid):
            cells = []
            for j, cell in enumerate(row):
                if hide_ships and cell == "N":
                    cells.append("~")
                else:
                    cells.append(cell)
            lines.append(f"{i} | " + " ".join(cells))

        return "\n".join(lines)
