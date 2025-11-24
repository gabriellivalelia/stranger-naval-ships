"""Classe Ship - representa um navio no jogo de batalha naval"""

import pygame


class Ship:
    """Representa um navio com posição, tamanho e estado"""

    def __init__(self, name, size, image_path=None):
        self._name = name
        self._size = size
        self._positions = []  # Lista de tuplas (linha, coluna)
        self._hits = set()  # Posições que foram atingidas
        self._image_path = image_path
        self._images = []  # Lista de superfícies pygame para cada segmento
        self._horizontal = True  # Orientação padrão

        if image_path:
            self._load_images()

    # Propriedades de acesso
    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def positions(self):
        return self._positions

    @property
    def hits(self):
        return self._hits

    @property
    def horizontal(self):
        return self._horizontal

    def _load_images(self):
        """Carrega imagens dos segmentos do navio"""
        try:
            # Carrega imagem para cada segmento do navio
            for i in range(self._size):
                segment_path = f"{self._image_path}_segment_{i + 1}.jpg"
                try:
                    img = pygame.image.load(segment_path)
                    self._images.append(img)
                except Exception:
                    # Tenta imagem base
                    try:
                        img = pygame.image.load(f"{self._image_path}.jpg")
                        self._images.append(img)
                    except Exception:
                        # Cria retângulo colorido como placeholder
                        surf = pygame.Surface((40, 40))
                        surf.fill((100, 100, 100))
                        self._images.append(surf)
                        print(
                            f"Aviso: Não foi possível carregar segmento {i + 1} para {self._name}"
                        )
        except Exception as e:
            print(f"Não foi possível carregar imagens para {self._name}: {e}")

    def place(self, positions):
        """Posiciona o navio nas posições especificadas"""
        if len(positions) != self._size:
            raise ValueError(f"Navio {self._name} precisa de {self._size} posições")
        self._positions = positions

        # Determina orientação baseada nas posições
        if len(positions) >= 2:
            self._horizontal = positions[0][0] == positions[1][0]

    def get_image(self, segment_index, cell_size=40):
        """Obtém imagem redimensionada para um segmento específico, rotacionada se vertical"""
        if segment_index < len(self._images):
            img = self._images[segment_index]
            img = pygame.transform.scale(img, (cell_size, cell_size))

            # Rotaciona -90 graus (270 graus) se o navio estiver vertical
            if not self._horizontal:
                img = pygame.transform.rotate(img, -90)

            return img
        return None

    def receive_attack(self, position):
        """Registra um ataque em uma posição. Retorna True se acertar"""
        if position in self._positions:
            self._hits.add(position)
            print(
                f"[Ship {self._name}] Hit at {position}! Hits: {len(self._hits)}/{self._size}"
            )
            return True
        return False

    def is_destroyed(self):
        """Verifica se o navio foi completamente destruído"""
        destroyed = len(self._hits) == self._size
        print(
            f"[Ship {self._name}] is_destroyed called: {destroyed} (hits: {len(self._hits)}/{self._size})"
        )
        return destroyed

    def __repr__(self):
        """Representação em string do navio para debug"""
        return f"Ship({self._name}, size={self._size}, hits={len(self._hits)}/{self._size})"
