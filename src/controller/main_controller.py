import pygame

from view.game_over_screen import GameOverScreen
from view.home_screen import HomeScreen
from view.play_screen import PlayScreen
from view.prepare_screen import PrepareScreen
from view.ranking_screen import RankingScreen
from view.session_screen import SessionScreen


# Telas: "home", "play", "ranking", "config", "exit", "login", "session", "prepare", "game_over"
class MainController:
    def __init__(self):
        pygame.init()
        self._current_screen = "home"
        self._screen = HomeScreen()
        self._running = True
        self._prepared_player = None  # Armazena jogador da PrepareScreen
        self._current_user = None  # Usuário atualmente logado
        self._guest_mode = (
            False  # Indica se está jogando como convidado (sem salvar ranking)
        )
        self._game_over_data = (
            None  # Armazena dados do game over (vitória, estatísticas)
        )

    def run(self):
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    # Passa todos os eventos para o handle_event da tela, se existir
                    handler = getattr(self._screen, "handle_event", None)
                    if callable(handler):
                        next_screen = handler(event)
                        if next_screen:
                            self._handle_navigation(next_screen)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Fallback para manipulação antiga de cliques para telas sem handle_event
                        self._handle_click(event)

            updater = getattr(self._screen, "update", None)
            if callable(updater):
                updater()

            self._screen.draw()
            self._screen.clock.tick(60)
        pygame.quit()

    def _handle_click(self, event):
        """Manipulador fallback para telas sem método handle_event"""
        next_screen = None

        checker = getattr(self._screen, "check_click", None)
        if callable(checker):
            next_screen = checker(event.pos)
        else:
            checker = getattr(self._screen, "_verify_click", None)
            next_screen = checker(event.pos) if callable(checker) else None

        if next_screen:
            self._handle_navigation(next_screen)

    def _handle_navigation(self, screen_result):
        """Gerencia navegação baseado no que a tela retornou.

        screen_result pode ser:
         - uma string simples: nome da próxima tela
         - uma tupla (nome_tela, dados): nome da tela e dados associados
        """
        if isinstance(screen_result, tuple):
            screen_name, data = screen_result
        else:
            screen_name = screen_result
            data = None

        if screen_name == "exit":
            self._running = False
            return

        if screen_name == "home":
            # Reseta usuário e modo guest apenas ao voltar para home
            self._current_user = None
            self._guest_mode = False
            self._change_screen("home")
            return

        if screen_name == "login":
            # Abre tela de login
            self._change_screen("login")
            return

        if screen_name == "login_success":
            # Login bem-sucedido, define usuário atual e vai para tela de preparação
            if data:
                self._current_user = data
                self._guest_mode = False
            self._change_screen("prepare")
            return

        if screen_name == "session":
            self._change_screen("session")
            return

        if screen_name == "prepare":
            # Se data é None, significa modo convidado
            if data is None:
                self._guest_mode = True
                self._current_user = None
            self._change_screen("prepare")
            return

        if screen_name == "ranking":
            # Se data fornecido, é o nome de usuário do login
            if data:
                self._current_user = data
                self._guest_mode = False
            self._change_screen("ranking")
            return

        if screen_name == "play":
            # Armazena jogador preparado se fornecido
            if data:
                self._prepared_player = data
            self._change_screen("play")
            return

        if screen_name == "game_over":
            # Tela de game over precisa dos dados (vitória, estatísticas)
            if data:
                self._game_over_data = data  # Armazena para _change_screen
            self._change_screen("game_over")
            return

    def _change_screen(self, screen_name):
        # Para música ao sair da tela home, play ou game_over
        if (
            (self._current_screen == "home" and screen_name != "home")
            or (self._current_screen == "play" and screen_name != "play")
            or (self._current_screen == "game_over" and screen_name != "game_over")
        ):
            pygame.mixer.music.stop()

        if screen_name == "home":
            self._screen = HomeScreen()
            self._prepared_player = None
            # Não reseta _current_user aqui, apenas ao sair do menu principal
        elif screen_name == "session":
            # Passa usuário anterior para SessionScreen se houver
            self._screen = SessionScreen(previous_user=self._current_user)
        elif screen_name == "play":
            # Cria controller de ranking apenas se não estiver em modo convidado
            ranking = None if self._guest_mode else self._create_ranking_controller()

            if self._prepared_player:
                self._screen = PlayScreen(
                    player=self._prepared_player,
                    ranking_controller=ranking,
                    current_user=self._current_user,
                )
            else:
                self._screen = PlayScreen(
                    ranking_controller=ranking, current_user=self._current_user
                )
        elif screen_name == "ranking":
            ranking_controller = self._create_ranking_controller()
            self._screen = RankingScreen(ranking_controller, self._current_user)
        elif screen_name == "login":
            from view.login_screen import LoginScreen

            ranking_controller = self._create_ranking_controller()
            self._screen = LoginScreen(ranking_controller)
        elif screen_name == "prepare":
            self._screen = PrepareScreen()
        elif screen_name == "game_over":
            # Usa dados armazenados de game over
            if self._game_over_data:
                won, stats = self._game_over_data
                self._screen = GameOverScreen(won, stats)
                self._game_over_data = None  # Limpa após uso
            else:
                # Fallback se nenhum dado foi fornecido
                print("Aviso: tela game_over criada sem dados")
                self._change_screen("home")
                return

        self._current_screen = screen_name

    def _create_ranking_controller(self):
        """Método factory para criar instâncias de RankingController."""
        import os

        from controller.ranking_controller import RankingController

        mongo_uri = os.environ.get("MONGO_URI")
        return RankingController(mongo_uri=mongo_uri)
