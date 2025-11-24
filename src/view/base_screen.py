from abc import ABC, abstractmethod

import pygame


class BaseScreen(ABC):
    def __init__(self, title: str = "Stranger Naval Ships"):
        """Inicializa tela base com atributos comuns.

        Args:
            width: Largura da tela em pixels (padrão: 1400)
            height: Altura da tela em pixels (padrão: 700)
            title: Título da janela (padrão: "Stranger Naval Ships")
        """
        self._width = 1400
        self._height = 900
        self._screen = pygame.display.set_mode((self._width, self._height))
        self._clock = pygame.time.Clock()
        pygame.display.set_caption(title)

        # Carrega fundo animado (comum a todas as telas)
        self._bg_surfaces = []
        self._bg_index = 0
        self._bg_last_switch = pygame.time.get_ticks()
        self._bg_switch_interval = 500

        try:
            bg_off = pygame.image.load("src/assets/home_screen_bg/off.png")
            bg_on = pygame.image.load("src/assets/home_screen_bg/on.png")
            bg_off = pygame.transform.scale(bg_off, (self._width, self._height))
            bg_on = pygame.transform.scale(bg_on, (self._width, self._height))
            self._bg_surfaces = [bg_off, bg_on]
        except Exception as e:
            print(f"Aviso: Não foi possível carregar imagens de fundo: {e}")
            # Cria gradiente como fallback
            grad = pygame.Surface((self._width, self._height))
            for y in range(self._height):
                t = y / max(1, self._height - 1)
                r = int(6 + (20 - 6) * t)
                g = int(12 + (50 - 12) * t)
                b = int(30 + (90 - 30) * t)
                pygame.draw.line(grad, (r, g, b), (0, y), (self._width, y))
            self._bg_surfaces = [grad]

    @abstractmethod
    def draw(self) -> None:
        """Desenha o conteúdo da tela. Deve ser implementado por todas as subclasses.

        Este método deve lidar com toda a lógica de renderização da tela.
        Deve terminar com pygame.display.flip() para atualizar o display.
        """
        pass

    def update(self) -> None:
        """Atualiza estado da tela (opcional, chamado a cada frame). """
        if len(self._bg_surfaces) > 1:
            current_time = pygame.time.get_ticks()
            if current_time - self._bg_last_switch >= self._bg_switch_interval:
                self._bg_index = (self._bg_index + 1) % len(self._bg_surfaces)
                self._bg_last_switch = current_time

    def handle_event(self, event: pygame.event.Event):
        """Trata eventos do pygame (opcional).

        Retorna um nome de tela (str) para navegar para outra tela,
        ou uma tupla (screen_name, data) para passar dados para próxima tela.

        Args:
            event: Objeto de evento Pygame

        Returns:
            str | tuple | None: Nome da tela para navegar, tupla com dados, ou None
        """
        # Comportamento padrão: delega clique esquerdo para check_click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.check_click(event.pos)
        return None

    def check_click(self, pos: tuple[int, int]):
        """Trata cliques do mouse na posição dada (opcional).
        Args:
            pos: Tupla de posição (x, y) do mouse

        Returns:
            str | tuple | None: Nome da tela para navegar, tupla com dados, ou None
        """
        return None

    def get_center_pos(self, width: int, height: int) -> tuple[int, int]:
        """Calcula posição para centralizar um elemento na tela.

        Args:
            width: Largura do elemento
            height: Altura do elemento

        Returns:
            Tupla de posição (x, y) para centralizar o elemento
        """
        x = (self._width - width) // 2
        y = (self._height - height) // 2
        return (x, y)

    def is_mouse_over(self, rect: pygame.Rect) -> bool:
        """Verifica se o mouse está sobre um retângulo.

        Args:
            rect: Retângulo para verificar

        Returns:
            True se o mouse está sobre o retângulo
        """
        return rect.collidepoint(pygame.mouse.get_pos())

    def draw_background(self) -> None:
        """Desenha o fundo animado."""
        if self._bg_surfaces:
            self._screen.blit(self._bg_surfaces[self._bg_index], (0, 0))
        else:
            self._screen.fill((0, 0, 0))

    @property
    def width(self) -> int:
        """Obtém largura da tela."""
        return self._width

    @property
    def height(self) -> int:
        """Obtém altura da tela."""
        return self._height

    @property
    def screen(self) -> pygame.Surface:
        """Obtém surface da tela do pygame."""
        return self._screen

    @property
    def clock(self) -> pygame.time.Clock:
        """Obtém relógio do pygame."""
        return self._clock
