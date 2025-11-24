import pygame

from model.entities.players.common_player import CommonPlayer
from model.entities.ships import (
    ArgylesVanShip,
    ChristmasShip,
    DemogorgonShip,
    LaboratoryShip,
    ScoopsAhoyShip,
)
from view.base_screen import BaseScreen


class PrepareScreen(BaseScreen):
    """Tela para o jogador posicionar navios antes da partida começar.

    Controles:
    - Clique esquerdo na grade do jogador: tenta posicionar navio atual na célula clicada
    - Clique direito ou tecla 'r': alterna orientação (horizontal/vertical)
    - Botão 'Aleatorizar': posiciona navios automaticamente (usa CommonPlayer.colocar_navios)
    - Botão 'Iniciar': disponível quando todos os navios estão posicionados, retorna "play"
    - Botão 'Voltar': retorna "home"
    """

    def __init__(self):
        super().__init__("Prepare - Posicionar Navios")

        # board drawing config
        self._cell_size = 50
        self._offset_x = 100
        self._offset_y = 150
        self._board_size = 10

        # player model
        self._player = CommonPlayer("Você")

        # ships to place - using themed ship classes
        self._ships_to_place = [
            DemogorgonShip(),  # 5 cells
            ScoopsAhoyShip(),  # 4 cells
            ChristmasShip(),  # 3 cells
            ArgylesVanShip(),  # 3 cells
            LaboratoryShip(),  # 2 cells
        ]
        self._current_index = 0
        self._horizontal = True

        # Track key state to avoid repeated toggles
        self._r_key_pressed = False
        self._last_toggle_time = 0
        self._toggle_cooldown = 300  # milliseconds between toggles

        # UI
        self._message = "Clique no tabuleiro para posicionar o navio"
        self._create_buttons()

        # Load click sound
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

        # Load put sound (for placing ships)
        self._put_sound = None
        try:
            self._put_sound = pygame.mixer.Sound("src/assets/sounds/put.mp3")
            self._put_sound.set_volume(0.6)
        except Exception as e:
            print(f"Não foi possível carregar som de posicionamento: {e}")

    def _create_buttons(self):
        """Cria botões estilizados"""
        button_width = 220
        button_height = 60
        button_x = self._width - button_width - 100

        self._buttons = [
            {
                "text": "Aleatorizar",
                "rect": pygame.Rect(button_x, 250, button_width, button_height),
                "color": (100, 100, 200),
                "hover_color": (150, 150, 255),
                "action": "randomize",
            },
            {
                "text": "Iniciar",
                "rect": pygame.Rect(button_x, 330, button_width, button_height),
                "color": (50, 150, 50),
                "hover_color": (100, 200, 100),
                "action": "start",
                "enabled_check": True,
            },
            {
                "text": "Voltar",
                "rect": pygame.Rect(button_x, 410, button_width, button_height),
                "color": (139, 0, 0),
                "hover_color": (200, 0, 0),
                "action": "back",
            },
        ]

    def update(self):
        """Atualiza animação de fundo e trata teclado"""
        # Update base screen (background animation)
        super().update()

        # Handle orientation toggle via keyboard (with debouncing)
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            if not self._r_key_pressed:
                self._horizontal = not self._horizontal
                self._r_key_pressed = True
        else:
            self._r_key_pressed = False

    def draw(self):
        # Draw animated background
        self.draw_background()

        # Title with shadow
        title_font = pygame.font.Font(None, 70)
        title_text = "POSICIONE SEUS NAVIOS"

        # Shadow
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_x = self._width // 2 - shadow.get_width() // 2 + 3
        self._screen.blit(shadow, (shadow_x, 53))

        # Title
        title = title_font.render(title_text, True, (255, 215, 0))
        title_x = self._width // 2 - title.get_width() // 2
        self._screen.blit(title, (title_x, 50))

        # Draw board background
        board_bg = pygame.Rect(
            self._offset_x - 10,
            self._offset_y - 10,
            self._board_size * self._cell_size + 20,
            self._board_size * self._cell_size + 20,
        )
        bg_surface = pygame.Surface((board_bg.width, board_bg.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self._screen.blit(bg_surface, (board_bg.x, board_bg.y))
        pygame.draw.rect(self._screen, (139, 0, 0), board_bg, 4, border_radius=10)

        # Draw board grid
        for row in range(self._board_size):
            for col in range(self._board_size):
                x = self._offset_x + col * self._cell_size
                y = self._offset_y + row * self._cell_size
                rect = pygame.Rect(x, y, self._cell_size, self._cell_size)
                cell = self._player.board.grid[row][col]
                if cell == "~":
                    color = (0, 119, 190, 150)
                else:
                    color = (100, 100, 100, 200)

                cell_surface = pygame.Surface(
                    (self._cell_size, self._cell_size), pygame.SRCALPHA
                )
                cell_surface.fill(color)
                self._screen.blit(cell_surface, (x, y))
                pygame.draw.rect(self._screen, (255, 255, 255, 100), rect, 1)

        # Draw placed ships with their images
        self._draw_placed_ships()

        # Preview current ship under mouse (and show validity)
        mx, my = pygame.mouse.get_pos()
        preview = None
        if not self.all_ships_placed():
            preview = self._compute_preview(mx, my)
        if preview:
            preview_rects, valid = preview
            color = (50, 255, 50, 150) if valid else (255, 50, 50, 150)
            for rx, ry in preview_rects:
                rect = pygame.Rect(rx, ry, self._cell_size, self._cell_size)
                preview_surface = pygame.Surface(
                    (self._cell_size, self._cell_size), pygame.SRCALPHA
                )
                preview_surface.fill(color)
                self._screen.blit(preview_surface, (rx, ry))
                border_color = (50, 255, 50) if valid else (255, 50, 50)
                pygame.draw.rect(self._screen, border_color, rect, 3, border_radius=5)

        # Current ship info box
        info_box = pygame.Rect(
            self._offset_x,
            self._offset_y + self._board_size * self._cell_size + 30,
            600,
            80,
        )
        info_surface = pygame.Surface((600, 80), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 200))
        self._screen.blit(info_surface, (info_box.x, info_box.y))
        pygame.draw.rect(self._screen, (255, 215, 0), info_box, 3, border_radius=8)

        # Ship info text
        info_font = pygame.font.Font(None, 32)
        if self.all_ships_placed():
            info_text = "Todos os navios posicionados!"
            info_color = (100, 255, 100)
        else:
            ship = self._ships_to_place[self._current_index]
            orientation = "Horizontal" if self._horizontal else "Vertical"
            info_text = f"Navio: {ship.name} ({ship.size} celulas) - {orientation}"
            info_color = (255, 255, 255)

        info = info_font.render(info_text, True, info_color)
        self._screen.blit(info, (info_box.x + 20, info_box.y + 15))

        # Message
        msg_font = pygame.font.Font(None, 26)
        msg = msg_font.render(self._message, True, (255, 200, 100))
        self._screen.blit(msg, (info_box.x + 20, info_box.y + 50))

        # Draw buttons with hover effect
        button_font = pygame.font.Font(None, 36)
        mouse_pos = pygame.mouse.get_pos()

        for button in self._buttons:
            # Check if button should be enabled
            enabled = True
            if button.get("enabled_check"):
                enabled = len(self._player.board.ships) == len(self._ships_to_place)

            rect = button["rect"]

            if not enabled:
                color = (60, 60, 60)
            elif rect.collidepoint(mouse_pos) and enabled:
                color = button["hover_color"]
                # Shadow on hover
                shadow_rect = rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(
                    self._screen, (0, 0, 0, 128), shadow_rect, border_radius=8
                )
            else:
                color = button["color"]

            pygame.draw.rect(self._screen, color, rect, border_radius=8)
            pygame.draw.rect(self._screen, (255, 255, 255), rect, 3, border_radius=8)

            text_surf = button_font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            self._screen.blit(text_surf, text_rect)

        # Instructions box
        inst_box = pygame.Rect(self._width - 340, 500, 320, 120)
        inst_surface = pygame.Surface((320, 120), pygame.SRCALPHA)
        inst_surface.fill((0, 0, 0, 200))
        self._screen.blit(inst_surface, (inst_box.x, inst_box.y))
        pygame.draw.rect(self._screen, (100, 150, 255), inst_box, 2, border_radius=8)

        inst_font = pygame.font.Font(None, 22)
        instructions = [
            "Instrucoes:",
            "- Clique no tabuleiro para",
            "  posicionar o navio",
            "- Tecla R: Rotacionar",
            "- Clique direito: Rotacionar",
        ]

        y_offset = inst_box.y + 10
        for line in instructions:
            inst_text = inst_font.render(line, True, (255, 255, 255))
            self._screen.blit(inst_text, (inst_box.x + 15, y_offset))
            y_offset += 22

        pygame.display.flip()

    def _draw_placed_ships(self):
        """Desenha navios posicionados com suas imagens"""
        for ship in self._player.board.ships:
            # Sort positions by visual order
            # For horizontal ships: sort by column (left to right)
            # For vertical ships: sort by row (top to bottom)
            if ship.horizontal:
                sorted_positions = sorted(ship.positions, key=lambda p: p[1])
            else:
                sorted_positions = sorted(ship.positions, key=lambda p: p[0])

            # Draw each segment with corresponding image index
            for i, pos in enumerate(sorted_positions):
                row, col = pos
                x = self._offset_x + col * self._cell_size
                y = self._offset_y + row * self._cell_size

                # Get ship image for this segment (i is the correct index)
                img = ship.get_image(i, self._cell_size)
                if img:
                    self._screen.blit(img, (x, y))

    def _compute_preview(self, mx, my):
        # if mouse over board, compute rectangle positions for preview
        if not (
            self._offset_x <= mx < self._offset_x + self._board_size * self._cell_size
            and self._offset_y
            <= my
            < self._offset_y + self._board_size * self._cell_size
        ):
            return None
        if self.all_ships_placed():
            return None
        col = (mx - self._offset_x) // self._cell_size
        row = (my - self._offset_y) // self._cell_size
        ship = self._ships_to_place[self._current_index]
        rects = []
        positions = []
        for i in range(ship.size):
            if self._horizontal:
                r = row
                c = col + i
            else:
                r = row + i
                c = col
            # compute top-left pixel
            rx = self._offset_x + c * self._cell_size
            ry = self._offset_y + r * self._cell_size
            rects.append((rx, ry))
            positions.append((r, c))

        # validity check: ensure all positions are inside board and unoccupied
        valid = True
        for r, c in positions:
            if r < 0 or c < 0 or r >= self._board_size or c >= self._board_size:
                valid = False
                break
            if self._player.board.grid[r][c] != "~":
                valid = False
                break

        return (rects, valid)

    def all_ships_placed(self):
        """Retorna True quando todos os navios foram posicionados (seja via
        posicionamento manual ou aleatorização)."""
        return self._current_index >= len(self._ships_to_place) or len(
            self._player.board.ships
        ) >= len(self._ships_to_place)

    def check_click(self, pos):
        x, y = pos
        # buttons
        for button in self._buttons:
            if button["rect"].collidepoint(pos):
                # Play click sound
                if self._click_sound:
                    self._click_sound.play()

                action = button.get("action")

                if action == "randomize":
                    # reset and auto-place
                    self._player.board = self._player.board.__class__()
                    self._player.place_ships()

                    # Play put sound for randomization
                    if self._put_sound:
                        self._put_sound.play()

                    # mark all as placed
                    self._current_index = len(self._ships_to_place)
                    self._message = "Navios posicionados aleatoriamente"
                    return None

                if action == "start":
                    if len(self._player.board.ships) == len(self._ships_to_place):
                        # Store player in MainController for PlayScreen to use
                        return ("play", self._player)
                    else:
                        self._message = "Coloque todos os navios antes de iniciar"
                        return None

                if action == "back":
                    return "home"

        # click on board: try to place
        if (
            self._offset_x <= x < self._offset_x + self._board_size * self._cell_size
            and self._offset_y
            <= y
            < self._offset_y + self._board_size * self._cell_size
        ):
            if self.all_ships_placed():
                self._message = "Todos os navios já foram posicionados"
                return None

            col = (x - self._offset_x) // self._cell_size
            row = (y - self._offset_y) // self._cell_size
            ship = self._ships_to_place[self._current_index]

            # Try to add the ship
            try:
                self._player.board.add_ship(ship, row, col, horizontal=self._horizontal)

                # Play put sound when ship is successfully placed
                if self._put_sound:
                    self._put_sound.play()

                # Only increment if successfully added
                self._current_index += 1
                if self._current_index >= len(self._ships_to_place):
                    self._message = "Todos os navios posicionados"
                else:
                    self._message = (
                        "Navio posicionado. Clique para posicionar o próximo"
                    )
            except ValueError as e:
                # Ship was not added, don't increment index
                self._message = f"Posição inválida: {e}"
            return None

        return None

    def handle_event(self, event):
        """Trata eventos do mouse do controller. Retorna um nome de tela se navegação for solicitada."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # right-click toggles orientation
                current_time = pygame.time.get_ticks()
                if current_time - self._last_toggle_time > self._toggle_cooldown:
                    self._horizontal = not self._horizontal
                    self._last_toggle_time = current_time
                    orientation = "Horizontal" if self._horizontal else "Vertical"
                    self._message = f"Orientação: {orientation}"
                return None
            if event.button == 1:  # left click -> delegate to check_click
                return self.check_click(event.pos)
        return None
