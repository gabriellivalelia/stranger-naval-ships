import os

import pygame

from controller.ranking_controller import RankingController
from view.game_over_screen import GameOverScreen
from view.home_screen import HomeScreen
from view.play_screen import PlayScreen
from view.prepare_screen import PrepareScreen
from view.ranking_screen import RankingScreen
from view.session_screen import SessionScreen


# Screens: "home", "play", "ranking", "config", "exit", "login", "session", "prepare", "game_over"
class MainController:
    def __init__(self):
        pygame.init()
        self.current_screen = "home"
        self.screen = HomeScreen()
        self.running = True
        self.prepared_player = None  # Store player from PrepareScreen
        self.current_user = None  # Currently logged in user
        self.guest_mode = False  # Track if playing as guest (no ranking save)

        # Initialize RankingController with optional MongoDB
        mongo_uri = os.environ.get("MONGO_URI")
        self.ranking_controller = RankingController(mongo_uri=mongo_uri)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    # Pass all events to the screen's handle_event if it exists
                    handler = getattr(self.screen, "handle_event", None)
                    if callable(handler):
                        next_screen = handler(event)
                        if next_screen:
                            self._handle_navigation(next_screen)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Fallback to old click handling for screens without handle_event
                        self._handle_click(event)

            updater = getattr(self.screen, "update", None)
            if callable(updater):
                updater()

            self.screen.draw()
            self.screen.clock.tick(60)
        pygame.quit()

    def _handle_click(self, event):
        """Fallback handler for screens without handle_event method"""
        next_screen = None

        checker = getattr(self.screen, "check_click", None)
        if callable(checker):
            next_screen = checker(event.pos)
        else:
            checker = getattr(self.screen, "_verify_click", None)
            next_screen = checker(event.pos) if callable(checker) else None

        if next_screen:
            self._handle_navigation(next_screen)

    def _handle_navigation(self, next_screen):
        """Handle navigation between screens"""
        if next_screen:
            if isinstance(next_screen, tuple):
                screen_name, data = next_screen

                # Handle different tuple returns
                if screen_name == "ranking":
                    # User logged in, data is username
                    self.current_user = data
                    self.guest_mode = False  # Not guest if logged in
                    self._change_screen("ranking")
                elif screen_name == "ranking_refresh":
                    # Logoff, data is None
                    self.current_user = data
                    self._change_screen("ranking")
                elif screen_name == "login_success":
                    # User logged in from session screen, data is username
                    self.current_user = data
                    self.guest_mode = False
                    self._change_screen("prepare")
                elif screen_name == "game_over":
                    # Game ended, data is (won, stats)
                    won, stats = data
                    self.screen = GameOverScreen(won, stats)
                    self.current_screen = "game_over"
                    return  # Don't call _change_screen
                elif screen_name == "prepare":
                    # From session screen: data is None for guest mode
                    if data is None:
                        self.guest_mode = True
                        self.current_user = None
                    self._change_screen("prepare")
                elif screen_name == "exit":
                    self.running = False
                else:
                    # Prepare screen returning player data
                    self.prepared_player = data
                    self._change_screen(screen_name)
            elif next_screen == "exit":
                self.running = False
            else:
                self._change_screen(next_screen)

    def _change_screen(self, screen_name):
        if screen_name == "home":
            self.screen = HomeScreen()
            self.prepared_player = None
            self.guest_mode = False  # Reset guest mode
        elif screen_name == "session":
            self.screen = SessionScreen()
        elif screen_name == "play":
            # Pass prepared player, ranking controller (only if not guest) and current user
            ranking = None if self.guest_mode else self.ranking_controller

            if self.prepared_player:
                self.screen = PlayScreen(
                    player=self.prepared_player,
                    ranking_controller=ranking,
                    current_user=self.current_user,
                )
            else:
                self.screen = PlayScreen(
                    ranking_controller=ranking, current_user=self.current_user
                )
        elif screen_name == "ranking":
            self.screen = RankingScreen(self.ranking_controller, self.current_user)
        elif screen_name == "login":
            from view.login_screen import LoginScreen

            # Determine where to return after login
            return_to = "ranking" if self.current_screen == "ranking" else "prepare"
            self.screen = LoginScreen(self.ranking_controller, return_to=return_to)
        elif screen_name == "prepare":
            self.screen = PrepareScreen()
        self.current_screen = screen_name
