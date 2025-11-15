from abc import ABC, abstractmethod

import pygame


class BaseScreen(ABC):
    def __init__(self, title: str = "Stranger Naval Ships"):
        """Initialize base screen with common attributes.

        Args:
            width: Screen width in pixels (default: 1400)
            height: Screen height in pixels (default: 700)
            title: Window title (default: "Stranger Naval Ships")
        """
        self.width = 1400
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(title)

    @abstractmethod
    def draw(self) -> None:
        """Draw the screen content. Must be implemented by all subclasses.

        This method should handle all rendering logic for the screen.
        Should end with pygame.display.flip() to update the display.
        """
        pass

    def update(self) -> None:
        """Update screen state (optional, called every frame).

        Override this method to add per-frame logic like animations,
        timers, or state updates that don't depend on events.
        """
        pass

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events (optional).

        Override this to handle keyboard, mouse, or other events.
        Return a screen name (str) to navigate to another screen,
        or a tuple (screen_name, data) to pass data to next screen.

        Args:
            event: Pygame event object

        Returns:
            str | tuple | None: Screen name to navigate to, tuple with data, or None
        """
        # Default behavior: delegate left-click to check_click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.check_click(event.pos)
        return None

    def check_click(self, pos: tuple[int, int]):
        """Handle mouse clicks at given position (optional).

        Override this for simple click handling. For more complex event
        handling (right-click, keyboard), override handle_event instead.

        Args:
            pos: Tuple of (x, y) mouse position

        Returns:
            str | tuple | None: Screen name to navigate to, tuple with data, or None
        """
        return None

    def get_center_pos(self, width: int, height: int) -> tuple[int, int]:
        """Calculate position to center an element on screen.

        Args:
            width: Element width
            height: Element height

        Returns:
            Tuple of (x, y) position to center the element
        """
        x = (self.width - width) // 2
        y = (self.height - height) // 2
        return (x, y)

    def is_mouse_over(self, rect: pygame.Rect) -> bool:
        """Check if mouse is currently over a rectangle.

        Args:
            rect: Rectangle to check

        Returns:
            True if mouse is over the rectangle
        """
        return rect.collidepoint(pygame.mouse.get_pos())
