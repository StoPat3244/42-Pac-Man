
def eat_pac_gum(
    pacman_position: tuple[int, int],
    pac_gums: list[tuple[int, int]],
) -> bool:
    if pacman_position in pac_gums:
        pac_gums.remove(pacman_position)
        return True

    return False


def eat_pacman(
    pacman_position: tuple[int, int],
    pac_gums: list[tuple[int, int]],
) -> bool:
    if pacman_position in pac_gums:
        pac_gums.remove(pacman_position)
        return True

    return False


def eat_ghost(
    pacman_position: tuple[int, int],
    pac_gums: list[tuple[int, int]],
) -> bool:
    if pacman_position in pac_gums:
        pac_gums.remove(pacman_position)
        return True

    return False
