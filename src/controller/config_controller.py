"""ConfigController - gerencia configurações do jogo"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigController:
    """Controller responsável por gerenciar configurações do jogo"""

    # Default settings
    DEFAULT_CONFIG = {
        "audio": {
            "music_enabled": True,
            "music_volume": 0.7,
            "sfx_enabled": True,
            "sfx_volume": 0.8,
        },
        "graphics": {
            "fullscreen": False,
            "resolution_width": 1400,
            "resolution_height": 700,
            "show_fps": False,
        },
        "gameplay": {
            "ai_difficulty": "medium",  # easy, medium, hard
            "animation_speed": "normal",  # slow, normal, fast
            "show_hints": True,
            "auto_save": True,
        },
        "player": {
            "default_name": "Jogador",
            "color_scheme": "default",  # default, dark, light
        },
    }

    def __init__(self, config_file: str = "data/config.json"):
        """
        Inicializa o controller de configurações.

        Args:
            config_file: Caminho para o arquivo JSON de configurações
        """
        self.config_file = Path(config_file)
        self.config = self._load_or_create_config()

    def _load_or_create_config(self) -> Dict[str, Any]:
        """Carrega configurações existentes ou cria novas com valores padrão"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                print(f"Erro ao carregar config: {e}. Usando padrões.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create new config file with defaults
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _merge_configs(
        self, default: Dict[str, Any], loaded: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mescla configurações carregadas com padrões.
        Garante que todas as chaves padrão existam.
        """
        result = default.copy()
        for key, value in loaded.items():
            if isinstance(value, dict) and key in result:
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Salva configurações no arquivo JSON"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
            return False

    def get(self, key_path: str) -> Optional[Any]:
        """
        Obtém um valor de configuração usando notação de ponto.

        Args:
            key_path: Caminho da chave (ex: "audio.music_volume")

        Returns:
            Valor da configuração ou None se não existir

        Example:
            >>> config.get("audio.music_volume")
            0.7
        """
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def set(self, key_path: str, value: Any) -> bool:
        """
        Define um valor de configuração usando notação de ponto.

        Args:
            key_path: Caminho da chave (ex: "audio.music_volume")
            value: Novo valor

        Returns:
            True se salvou com sucesso

        Example:
            >>> config.set("audio.music_volume", 0.5)
            True
        """
        keys = key_path.split(".")
        current = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the value
        current[keys[-1]] = value
        return self._save_config(self.config)

    def get_audio_config(self) -> Dict[str, Any]:
        """Retorna todas as configurações de áudio"""
        return self.config.get("audio", {})

    def get_graphics_config(self) -> Dict[str, Any]:
        """Retorna todas as configurações gráficas"""
        return self.config.get("graphics", {})

    def get_gameplay_config(self) -> Dict[str, Any]:
        """Retorna todas as configurações de gameplay"""
        return self.config.get("gameplay", {})

    def get_player_config(self) -> Dict[str, Any]:
        """Retorna todas as configurações do jogador"""
        return self.config.get("player", {})

    def set_music_volume(self, volume: float) -> bool:
        """Define o volume da música (0.0 a 1.0)"""
        volume = max(0.0, min(1.0, volume))
        return self.set("audio.music_volume", volume)

    def set_sfx_volume(self, volume: float) -> bool:
        """Define o volume dos efeitos sonoros (0.0 a 1.0)"""
        volume = max(0.0, min(1.0, volume))
        return self.set("audio.sfx_volume", volume)

    def toggle_music(self) -> bool:
        """Liga/desliga a música"""
        enabled = self.get("audio.music_enabled")
        return self.set("audio.music_enabled", not enabled)

    def toggle_sfx(self) -> bool:
        """Liga/desliga os efeitos sonoros"""
        enabled = self.get("audio.sfx_enabled")
        return self.set("audio.sfx_enabled", not enabled)

    def set_ai_difficulty(self, difficulty: str) -> bool:
        """
        Define a dificuldade da IA.

        Args:
            difficulty: "easy", "medium", ou "hard"
        """
        if difficulty not in ["easy", "medium", "hard"]:
            return False
        return self.set("gameplay.ai_difficulty", difficulty)

    def set_resolution(self, width: int, height: int) -> bool:
        """Define a resolução da janela"""
        self.set("graphics.resolution_width", width)
        return self.set("graphics.resolution_height", height)

    def toggle_fullscreen(self) -> bool:
        """Liga/desliga modo fullscreen"""
        fullscreen = self.get("graphics.fullscreen")
        return self.set("graphics.fullscreen", not fullscreen)

    def reset_to_defaults(self) -> bool:
        """Restaura todas as configurações para os valores padrão"""
        self.config = self.DEFAULT_CONFIG.copy()
        return self._save_config(self.config)

    def export_config(self) -> Dict[str, Any]:
        """Exporta todas as configurações como dicionário"""
        return self.config.copy()

    def import_config(self, config: Dict[str, Any]) -> bool:
        """
        Importa configurações de um dicionário.

        Args:
            config: Dicionário de configurações

        Returns:
            True se importou e salvou com sucesso
        """
        self.config = self._merge_configs(self.DEFAULT_CONFIG, config)
        return self._save_config(self.config)
