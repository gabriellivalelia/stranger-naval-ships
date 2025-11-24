"""Laboratory Ship - navio temático de 2 células (Destroyer)"""

from model.entities.ship import Ship


class LaboratoryShip(Ship):
    """Navio temático baseado no laboratório de Hawkins (3 células)"""

    def __init__(self):
        super().__init__(
            name="Hawkins Lab", size=3, image_path="src/assets/ships/laboratory"
        )
