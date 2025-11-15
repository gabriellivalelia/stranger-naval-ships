import pygame

from view.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    def __init__(self):
        super().__init__("Menu - Stranger Things Naval Battle")
        self.font = pygame.font.Font(None, 48)
        self.buttons = self._create_buttons()
        self.bg_paths = [
            "src/assets/home_screen_bg/off.png",
            "src/assets/home_screen_bg/on.png",
        ]

        self._bg_surfaces = []
        self._bg_index = 0
        self._bg_switch_interval = 500
        self._bg_last_switch = pygame.time.get_ticks()

        for p in self.bg_paths:
            try:
                img = pygame.image.load(p)
                img = pygame.transform.scale(img, (self.width, self.height))
                try:
                    img = img.convert()
                except Exception:
                    img = img.convert_alpha()
                self._bg_surfaces.append(img)
            except Exception:
                # ignore bad paths, continue with others
                continue

    def _create_buttons(self):
        buttons = {
            "Jogar": pygame.Rect(300, 250, 200, 50),
            "Ranking": pygame.Rect(300, 320, 200, 50),
            "Sair": pygame.Rect(300, 390, 200, 50),
        }
        return buttons

    def draw(self):
        if self._bg_surfaces:
            now = pygame.time.get_ticks()
            if now - self._bg_last_switch >= self._bg_switch_interval:
                self._bg_index = (self._bg_index + 1) % len(self._bg_surfaces)
                self._bg_last_switch = now

            self.screen.blit(self._bg_surfaces[self._bg_index], (0, 0))
        else:
            self.screen.fill((20, 20, 50))

        title = self.font.render("BATALHA NAVAL - STRANGER THINGS", True, (255, 0, 0))
        self.screen.blit(title, (60, 100))

        button_font = pygame.font.Font(None, 36)
        for text, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (255, 0, 0), rect, border_radius=10)
            txt = button_font.render(text, True, (255, 255, 255))
            self.screen.blit(txt, (rect.x + 60, rect.y + 10))
        pygame.display.flip()

    def check_click(self, pos):
        for text, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if text == "Jogar":
                    return "session"  # Go to session screen first
                elif text == "Ranking":
                    return "ranking"
                elif text == "Sair":
                    return "exit"
        return None
