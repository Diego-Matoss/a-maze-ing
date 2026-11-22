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
