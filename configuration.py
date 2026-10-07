import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Dict, List


_DEFAULT_VERSION = {
    "h_score": "./data/score.json", "lives": 3, "pacgum": 100,
    "points_per_pacgum": 10, "points_per_super_pacgum": 50,
    "points_per_ghost": 200, "seed": 42, "level_max_time": 90,
    "level": [{"width": 20, "height": 20}, {"width": 19, "height": 19},
              {"width": 18, "height": 18}, {"width": 17, "height": 17},
              {"width": 16, "height": 16}, {"width": 15, "height": 15},
              {"width": 14, "height": 14}, {"width": 13, "height": 13},
              {"width": 12, "height": 12}, {"width": 11, "height": 11}]}


@dataclass
class Level():
    width: int
    height: int

    def __post_init__(self) -> None:
        _check_int("width", self.width, min_exclusive=10, max_exclusive=50)
        _check_int("height", self.height, min_exclusive=10, max_exclusive=50)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Level":
        known_keys = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known_keys}
        return cls(**filtered)


def _check_int(key: str, value: Any, *, min_exclusive: int = None,
               min_inclusive: int = None, max_exclusive: int = None
               ) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(
            f"'{key}' must be an integer, received: {value}")
    if min_exclusive is not None and value <= min_exclusive:
        raise ValueError(
            f"'{key}' must be > {min_exclusive}, received: {value}")
    if min_inclusive is not None and value < min_inclusive:
        raise ValueError(
            f"'{key}' must be >= {min_inclusive}, received: {value}")
    if max_exclusive is not None and value >= max_exclusive:
        raise ValueError(
            f"'{key}' must be < {max_exclusive}, received: {value}")


@dataclass
class Configuration:
    """Global configuration of the game."""
    h_score: str
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    level: List[Level]
    cheat_mode = False
    default_version = False

    def __post_init__(self) -> None:
        self._check_h_score_path(self.h_score)
        _check_int("lives", self.lives, min_exclusive=0)
        _check_int("pacgum", self.pacgum, min_exclusive=0)
        _check_int("points_per_pacgum", self.points_per_pacgum,
                   min_inclusive=0)
        _check_int("points_per_super_pacgum", self.points_per_super_pacgum,
                   min_inclusive=0)
        _check_int("points_per_ghost", self.points_per_ghost, min_inclusive=0)
        self._check_seed(self.seed)
        _check_int("level_max_time", self.level_max_time, min_exclusive=0)
        self._check_levels(self.level)
        self._check_pacgum_capacity(self.pacgum, self.level)

    def _check_levels(self, level: Any) -> None:
        if not isinstance(level, list) or not level:
            raise ValueError("Value for 'level' not valid.")
        else:
            converted = []
            for item in self.level:
                if isinstance(item, Level):
                    converted.append(item)
                elif isinstance(item, dict):
                    converted.append(Level.from_dict(item))
                else:
                    raise ValueError("Value for 'level' not valid.")
            self.level = converted

    def _check_pacgum_capacity(self, pacgums: int,
                               level: Level | list["Level"]) -> None:
        levels = level if isinstance(level, list) else [level]
        for current_level in levels:
            if pacgums > (current_level.width * current_level.height - 18):
                raise ValueError(
                    "The number of pacgums is too high for the "
                    "size of the maze.")

    def _check_h_score_path(self, path: Any) -> None:
        if not isinstance(path, str):
            raise ValueError(
                f"'h_score' must be a string path, received: {path}")
        try:
            file_path = Path(path)
        except (TypeError, ValueError):
            raise ValueError(f"'h_score' is not a valid path: {path}")
        if file_path.suffix.lower() not in {".json", ".txt"}:
            raise ValueError(
                f"'h_score' must be a .json or .txt file, received: {path}")
        if file_path.exists() and file_path.is_dir():
            raise ValueError(f"'h_score' cannot be a directory: {path}")

    def _check_seed(self, value: Any) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"'seed' must be an integer, received: {value}")

    @staticmethod
    def _remove_comments(text: str) -> str:
        if text == "":
            return "{}"
        lines = []
        for line in text.splitlines():
            in_string = False
            escaped = False
            output = []
            for char in line:
                if char == '"' and not escaped:
                    in_string = not in_string
                if char == '#' and not in_string:
                    break
                output.append(char)
                escaped = char == '\\' and not escaped
            lines.append(''.join(output))
        return '\n'.join(lines)

    @classmethod
    def build_config(cls, filepath: str) -> "Configuration":
        try:
            config_path = Path(filepath).resolve()
            if config_path.suffix.lower() != ".json":
                raise ValueError(
                    f"Configuration file must be .json format: {config_path}")
            with open(filepath) as f:
                text = f.read()
            data = json.loads(cls._remove_comments(text))
        # poiche Configuratin e' una @dataclass
        # posso usare fields(cls) per avere info sui dati di classe
        # estrae solo i nomi delle variabili di classe. restituendo un set
            known_keys = {f.name for f in fields(cls)}
        # qui si crea un nuovo dizionario con solo le chiavi
        # che la classe conosce (e' case_sensitive)
            # controllo che ci siano [] oppure {} all inizio del json file
            if isinstance(data, list) and data:
                data = data[0]
            if not isinstance(data, dict):
                raise ValueError(
                    "The JSON root must be an object "
                    "(or a non-empty list starting with an object).")
            filtered = {k: v for k, v in data.items() if k in known_keys}
            # Controlla che h_score non coincida con il file di configurazione
            h_score = filtered.get("h_score")

            if h_score is not None:
                if not isinstance(h_score, str):
                    raise ValueError(
                        f"'h_score' must be a string. Received: {h_score}")
                h_score_path = Path(h_score).resolve()
                # h_score_path = (config_path.parent / h_score).resolve()
                if h_score_path == config_path:
                    raise ValueError(
                        "The h_score file cannot be the same as "
                        "the configuration file.")
            return cls(**filtered)
        except json.JSONDecodeError:
            print("[ERROR] Configuration file is not in a valid JSON format.")
            print("DEFAULT VERSION in use.")
        except Exception as e:
            print("[ERROR] ", e)
            print("DEFAULT VERSION in use.")
        config = cls(**_DEFAULT_VERSION)
        config.default_version = True
        return config
