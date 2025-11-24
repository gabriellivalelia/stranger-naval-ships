"""Christmas Ship - navio temático de 3 células (Cruzador)"""

from model.entities.ship import Ship


class ChristmasShip(Ship):
    """Navio temático baseado nas luzes de Natal de Stranger Things (3 células)"""

    def __init__(self):
        super().__init__(
            name="Christmas Lights", size=2, image_path="src/assets/ships/christmas"
        )
