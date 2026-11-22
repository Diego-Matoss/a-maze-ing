"""Parser for the A-maze-ing configuration file"""

from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Validated maze configuration.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell as (x, y).
        exit: Exit cell as (x, y).
        output_file: Path of the output file.
        perfect: Whether the maze must be perfect.
        seed: Random seed, or None for a random one.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def read_config_lines(path: str) -> list[str]:
    """Read a configuration file and return its raw lines.

    Args:
        path: Path to the configuration file.

    Returns:
        The lines of the file, in order.

    Raises:
        ConfigError: If the file cannot be read.
    """

    lines: list[str] = []

    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, ValueError) as e:
        raise ConfigError(f"Cannot read '{path}': {e}") from e

    return lines
