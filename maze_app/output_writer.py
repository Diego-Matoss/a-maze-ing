"""Write a generated maze and its solution to an output file."""

from typing import Protocol


class MazeLike(Protocol):
    """Minimal interface expected from a MazeGenerator instance."""

    grid: list[list[int]]
    entry: tuple[int, int]
    exit: tuple[int, int]
    path: str


def write_maze(maze: MazeLike, output_path: str) -> None:
    """Write the maze grid, coordinates, and shortest path to a file.

    Args:
        maze: Generated maze object exposing grid, entry, exit, and path.
        output_path: Destination file path.

    Raises:
        OSError: If the file cannot be opened or written.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for row in maze.grid:
            line = "".join(f"{cell:x}" for cell in row)
            f.write(line + "\n")

        f.write("\n")
        f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
        f.write(f"{maze.exit[0]},{maze.exit[1]}\n")
        f.write(f"{maze.path}\n")
