def find_center_position(
    maze: list[list[int]],
) -> tuple[int, int]:

    rows = len(maze)
    columns = len(maze[0])

    center = (
        rows // 2,
        columns // 2,
    )

    row, column = center

    if maze[row][column] != 15:
        return center

    # Search outward from the center
    for distance in range(1, max(rows, columns)):

        for r in range(
            max(0, row - distance),
            min(rows, row + distance + 1),
        ):
            for c in range(
                max(0, column - distance),
                min(columns, column + distance + 1),
            ):

                if maze[r][c] != 15:
                    return (r, c)

    raise ValueError("No valid cell found in maze.")


def find_corner_position(
    maze: list[list[int]],
    corner: str,
) -> tuple[int, int]:

    rows = len(maze)
    columns = len(maze[0])

    if corner == "top_left":
        start_row = 0
        start_column = 0

    elif corner == "top_right":
        start_row = 0
        start_column = columns - 1

    elif corner == "bottom_left":
        start_row = rows - 1
        start_column = 0

    elif corner == "bottom_right":
        start_row = rows - 1
        start_column = columns - 1

    else:
        raise ValueError(
            f"Unknown corner: {corner}"
        )

    # If the actual corner is valid, use it.
    if maze[start_row][start_column] != 15:
        return (start_row, start_column)

    # Search progressively farther from the corner.
    for distance in range(
        1,
        max(rows, columns),
    ):

        for row in range(rows):
            for column in range(columns):

                if (
                    abs(row - start_row) +
                    abs(column - start_column)
                    != distance
                ):
                    continue

                if maze[row][column] != 15:
                    return (row, column)

    raise ValueError(
        f"No valid cell found near {corner}"
    )
