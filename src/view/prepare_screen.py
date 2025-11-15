import pygame

from model.entities.players.common_player import CommonPlayer
from model.entities.ship import Ship
from view.base_screen import BaseScreen


class PrepareScreen(BaseScreen):
    """Screen to let the player place ships before the match starts.

    Controls:
    - Left click on player's grid: try place current ship at clicked cell
    - Right click or press 'r': toggle orientation (horizontal/vertical)
    - 'Randomize' button: auto-place ships (uses CommonPlayer.colocar_navios)
    - 'Start' button: available when all ships placed, returns "play"
    - 'Back' button: returns "home"
    """

    def __init__(self):
        super().__init__("Prepare - Posicionar Navios")

        # board drawing config
        self.cell_size = 40
        self.offset_x = 50
        self.offset_y = 80
        self.board_size = 10

        # player model
        self.player = CommonPlayer("Você")

        # ships to place (name, size) - same as CommonPlayer default
        self.ships_to_place = [
            ("Porta-Aviões", 5),
            ("Encouraçado", 4),
            ("Cruzador", 3),
            ("Submarino", 3),
            ("Destroyer", 2),
        ]
        self.current_index = 0
        self.horizontal = True

        # Track key state to avoid repeated toggles
        self.r_key_pressed = False
        self.last_toggle_time = 0
        self.toggle_cooldown = 300  # milliseconds between toggles

        # UI
        self.message = "Click on the board to place the current ship"
        self.buttons = {
            "randomize": pygame.Rect(self.width - 220, 100, 200, 40),
            "start": pygame.Rect(self.width - 220, 160, 200, 40),
            "back": pygame.Rect(self.width - 220, 220, 200, 40),
        }

    def draw(self):
        # background
        self.screen.fill((20, 30, 50))

        # draw player's board
        font = pygame.font.Font(None, 28)
        title = font.render("Posicione seus navios", True, (255, 255, 255))
        self.screen.blit(title, (self.offset_x, 20))

        for row in range(self.board_size):
            for col in range(self.board_size):
                x = self.offset_x + col * self.cell_size
                y = self.offset_y + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                cell = self.player.board.grid[row][col]
                if cell == "~":
                    color = (0, 119, 190)
                else:
                    color = (100, 100, 100)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 80), rect, 1)

        # preview current ship under mouse (and show validity)
        mx, my = pygame.mouse.get_pos()
        preview = None
        if not self.all_ships_placed():
            preview = self._compute_preview(mx, my)
        if preview:
            preview_rects, valid = preview
            color = (50, 200, 50) if valid else (200, 50, 50)
            for rx, ry in preview_rects:
                rect = pygame.Rect(rx, ry, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect, 3)

        # UI texts
        info_font = pygame.font.Font(None, 24)
        if self.all_ships_placed():
            info = info_font.render("All ships placed", True, (255, 255, 255))
        else:
            name, size = self.ships_to_place[self.current_index]
            info = info_font.render(
                f"Current: {name} (size {size}) - {'H' if self.horizontal else 'V'}",
                True,
                (255, 255, 255),
            )
        self.screen.blit(
            info, (self.offset_x, self.offset_y + self.board_size * self.cell_size + 10)
        )

        msg = info_font.render(self.message, True, (255, 200, 200))
        self.screen.blit(
            msg, (self.offset_x, self.offset_y + self.board_size * self.cell_size + 40)
        )

        # buttons
        for key, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (200, 50, 50), rect, border_radius=6)
            txt = info_font.render(key.capitalize(), True, (255, 255, 255))
            self.screen.blit(txt, (rect.x + 20, rect.y + 10))

        # Start button enabled only if all ships placed
        if len(self.player.board.ships) == len(self.ships_to_place):
            pygame.draw.rect(
                self.screen, (50, 200, 50), self.buttons["start"], border_radius=6
            )
            txt = info_font.render("Start", True, (0, 0, 0))
            self.screen.blit(
                txt, (self.buttons["start"].x + 20, self.buttons["start"].y + 10)
            )

        pygame.display.flip()

    def _compute_preview(self, mx, my):
        # if mouse over board, compute rectangle positions for preview
        if not (
            self.offset_x <= mx < self.offset_x + self.board_size * self.cell_size
            and self.offset_y <= my < self.offset_y + self.board_size * self.cell_size
        ):
            return None
        if self.all_ships_placed():
            return None
        col = (mx - self.offset_x) // self.cell_size
        row = (my - self.offset_y) // self.cell_size
        name, size = self.ships_to_place[self.current_index]
        rects = []
        positions = []
        for i in range(size):
            if self.horizontal:
                r = row
                c = col + i
            else:
                r = row + i
                c = col
            # compute top-left pixel
            rx = self.offset_x + c * self.cell_size
            ry = self.offset_y + r * self.cell_size
            rects.append((rx, ry))
            positions.append((r, c))

        # validity check: ensure all positions are inside board and unoccupied
        valid = True
        for r, c in positions:
            if r < 0 or c < 0 or r >= self.board_size or c >= self.board_size:
                valid = False
                break
            if self.player.board.grid[r][c] != "~":
                valid = False
                break

        return (rects, valid)

    def all_ships_placed(self):
        """Return True when all ships have been placed (either via manual
        placement or randomize)."""
        return self.current_index >= len(self.ships_to_place) or len(
            self.player.board.ships
        ) >= len(self.ships_to_place)

    def check_click(self, pos):
        x, y = pos
        # buttons
        for key, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if key == "randomize":
                    # reset and auto-place
                    self.player.board = self.player.board.__class__()
                    self.player.place_ships()
                    # mark all as placed
                    self.current_index = len(self.ships_to_place)
                    self.message = "Ships randomly placed"
                    return None
                if key == "start":
                    if len(self.player.board.ships) == len(self.ships_to_place):
                        # Store player in MainController for PlayScreen to use
                        return ("play", self.player)
                    else:
                        self.message = "Coloque todos os navios antes de iniciar"
                        return None
                if key == "back":
                    return "home"

        # click on board: try to place
        if (
            self.offset_x <= x < self.offset_x + self.board_size * self.cell_size
            and self.offset_y <= y < self.offset_y + self.board_size * self.cell_size
        ):
            if self.all_ships_placed():
                self.message = "All ships already placed"
                return None

            col = (x - self.offset_x) // self.cell_size
            row = (y - self.offset_y) // self.cell_size
            name, size = self.ships_to_place[self.current_index]

            # Create ship and try to add it
            ship = Ship(name, size)
            try:
                self.player.board.add_ship(ship, row, col, horizontal=self.horizontal)
                # Only increment if successfully added
                self.current_index += 1
                if self.current_index >= len(self.ships_to_place):
                    self.message = "All ships placed"
                else:
                    self.message = "Ship placed. Click to place the next one"
            except ValueError as e:
                # Ship was not added, don't increment index
                self.message = f"Invalid position: {e}"
            return None

        return None

    def update(self):
        # handle orientation toggle via keyboard (with debouncing to avoid rapid toggles)
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            if not self.r_key_pressed:
                self.horizontal = not self.horizontal
                self.r_key_pressed = True
        else:
            self.r_key_pressed = False

    def handle_event(self, event):
        """Handle mouse events from controller. Returns a screen name if navigation is requested."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # right-click toggles orientation
                current_time = pygame.time.get_ticks()
                if current_time - self.last_toggle_time > self.toggle_cooldown:
                    self.horizontal = not self.horizontal
                    self.last_toggle_time = current_time
                    orientation = "Horizontal" if self.horizontal else "Vertical"
                    self.message = f"Orientação: {orientation}"
                return None
            if event.button == 1:  # left click -> delegate to check_click
                return self.check_click(event.pos)
        return None
