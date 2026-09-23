from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

DEFAULT_H_SCORE = "./data/score.json"
DEFAULT_LIVES = 3
DEFAULT_PACGUM = 40
DEFAULT_POINTS_PER_PACGUM = 10
DEFAULT_POINTS_PER_SUPER_PACGUM = 50
DEFAULT_POINTS_PER_GHOST = 200
DEFAULT_SEED = 42
DEFAULT_LEVEL_MAX_TIME = 90
DEFAULT_WIDTH = 20
DEFAULT_HEIGHT = 20

FIXED_CLOSED_CELLS = 18 # 42 logo


def _validate(name: str, value: Any, validator: Callable[[Any], Any], default: Any) -> Any:
    try:
        return validator(value)
    except ValueError as exc:
        print(f"[Configuration] value '{name}' not valid: {exc} -> default {default!r} in use")
        return default


def _check_int(value: Any, *, min_exclusive: int = None, min_inclusive: int = None,
                max_exclusive: int = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"must be an integer, received: {value!r}")

    if min_exclusive is not None and value <= min_exclusive:
        raise ValueError(f"must be > {min_exclusive}, received: {value}")

    if min_inclusive is not None and value < min_inclusive:
        raise ValueError(f"must be >= {min_inclusive}, received: {value}")

    if max_exclusive is not None and value >= max_exclusive:
        raise ValueError(f"must be < {max_exclusive}, received: {value}")

    return value


def _check_seed(value: Any) -> Union[int, str]:
    if not isinstance(value, (int, str)) or isinstance(value, bool):
        raise ValueError(f"must be int or str, received: {value!r}")
    return value


def _available_cells(level: "Level") -> int:
    return level.width * level.height - FIXED_CLOSED_CELLS


def _check_h_score_path(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(f"must be a string, received: {value!r}")
    try:
        path = Path(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"is not valid path: {value!r}") from e
    return value


@dataclass
class Level:
    width: int
    height: int

    def __post_init__(self) -> None:
        self.width = _validate(
            "width", self.width,
            lambda v: _check_int(v, min_exclusive=10, max_exclusive=50),
            DEFAULT_WIDTH,
        )
        self.height = _validate(
            "height", self.height,
            lambda v: _check_int(v, min_exclusive=10, max_exclusive=50),
            DEFAULT_HEIGHT,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Level":
        known_keys = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known_keys}
        return cls(**filtered)


@dataclass
class Configuration:
    """Global configuration of the game."""
    h_score: str
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: Union[int, str]
    level_max_time: int
    level: List[Level]

    def __post_init__(self) -> None:
        self.h_score = _validate("h_score", self.h_score, _check_h_score_path, DEFAULT_H_SCORE)

        self.lives = _validate(
            "lives", self.lives, lambda v: _check_int(v, min_exclusive=0), DEFAULT_LIVES)

        self.pacgum = _validate(
            "pacgum", self.pacgum, lambda v: _check_int(v, min_exclusive=0), DEFAULT_PACGUM)

        self.points_per_pacgum = _validate(
            "points_per_pacgum", self.points_per_pacgum,
            lambda v: _check_int(v, min_inclusive=0), DEFAULT_POINTS_PER_PACGUM,)

        self.points_per_super_pacgum = _validate(
            "points_per_super_pacgum", self.points_per_super_pacgum,
            lambda v: _check_int(v, min_inclusive=0), DEFAULT_POINTS_PER_SUPER_PACGUM,)

        self.points_per_ghost = _validate(
            "points_per_ghost", self.points_per_ghost,
            lambda v: _check_int(v, min_inclusive=0), DEFAULT_POINTS_PER_GHOST,)

        self.seed = _validate("seed", self.seed, _check_seed, DEFAULT_SEED)

        self.level_max_time = _validate(
            "level_max_time", self.level_max_time,
            lambda v: _check_int(v, min_exclusive=0), DEFAULT_LEVEL_MAX_TIME,)

        if not isinstance(self.level, list) or not self.level:
            print(
                f"[Configuration] valore non valido per 'level': must be a list -> default in use"
                f"[{{'width': {DEFAULT_WIDTH}, 'height': {DEFAULT_HEIGHT}}}]"
            )
            self.level = [Level(DEFAULT_WIDTH, DEFAULT_HEIGHT)]
        else:
            converted = []
            for item in self.level:
                if isinstance(item, Level):
                    converted.append(item)
                elif isinstance(item, dict):
                    converted.append(Level.from_dict(item))
                else:
                    print(
                        f"[Configuration] key not valid in 'level': {item!r} "
                        f"-> default in use {{'width': {DEFAULT_WIDTH}, 'height': {DEFAULT_HEIGHT}}}"
                    )
                    converted.append(Level(DEFAULT_WIDTH, DEFAULT_HEIGHT))
            self.level = converted

            min_available = min(_available_cells(lvl) for lvl in self.level)
            safe_default = min(DEFAULT_PACGUM, min_available)

            def _check_pacgum_capacity(v: int) -> int:
                if v > min_available:
                    too_small = [
                        f"{lvl.width}x{lvl.height} (available cells: {_available_cells(lvl)})"
                        for lvl in self.level
                        if _available_cells(lvl) < v
                    ]
                    raise ValueError(
                        f"{v} numebrs of pacgum too high for the level: {', '.join(too_small)} "
                    )
                return v

        self.pacgum = _validate("pacgum", self.pacgum, _check_pacgum_capacity, safe_default)


    @classmethod
    def from_dict_to_class(cls, data: Dict[str, Any]) -> "Configuration":
        known_keys = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known_keys}
        return cls(**filtered)
