"""Argyle's Van Ship - navio temático de 3 células (Submarino)"""

from model.entities.ship import Ship


class ArgylesVanShip(Ship):
    """Navio temático baseado na van do Argyle (3 células)"""

    def __init__(self):
        super().__init__(
            name="Argyle's Van", size=3, image_path="src/assets/ships/argyles_van"
        )
