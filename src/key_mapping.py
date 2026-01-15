"""Keyboard mapping constants for game controls."""

import pygame

# moving
# 7 8 9
# 4 5 6
# 1 2 3


# MOVE_UP = pygame.K_w
# MOVE_DOWN = pygame.K_x
# MOVE_LEFT = pygame.K_a
# MOVE_RIGHT = pygame.K_d
# MOVE_WAIT = pygame.K_s
# MOVE_UP_LEFT = pygame.K_q
# MOVE_DOWN_LEFT = pygame.K_y
# MOVE_UP_RIGHT = pygame.K_e
# MOVE_DOWN_RIGHT = pygame.K_c

# TODO I think all this can be propagated down to the call points just using the modern pygame key constants
MOVE_UP: int = pygame.K_KP8
MOVE_DOWN: int = pygame.K_KP2
MOVE_LEFT: int = pygame.K_KP4
MOVE_RIGHT: int = pygame.K_KP6
MOVE_WAIT: int = pygame.K_KP5
MOVE_UP_LEFT: int = pygame.K_KP7
MOVE_DOWN_LEFT: int = pygame.K_KP1
MOVE_UP_RIGHT: int = pygame.K_KP9
MOVE_DOWN_RIGHT: int = pygame.K_KP3

MOVES: list[int] = [
    MOVE_UP,
    MOVE_DOWN,
    MOVE_RIGHT,
    MOVE_LEFT,
    MOVE_WAIT,
    MOVE_UP_LEFT,
    MOVE_DOWN_LEFT,
    MOVE_UP_RIGHT,
    MOVE_DOWN_RIGHT,
]

GAME_SAVE_QUIT: int = pygame.K_F8

ACTION_EQUIP: int = pygame.K_e
ACTION_PICKUP: int = pygame.K_COMMA  # PERIOD
ACTION_CAST: int = pygame.K_c
ACTION_DOWNSTAIRS: int = pygame.K_LESS
ACTION_UPSTAIRS: int = pygame.K_y
ACTION_TAKE_OFF: int = pygame.K_t
ACTION_DROP: int = pygame.K_d
ACTION_QUAFF: int = pygame.K_q
ACTION_READ: int = pygame.K_r
ACTION_CURSOR: int = pygame.K_i
ACTION_STATS: int = pygame.K_s

ACTION_FIRE: int = pygame.K_f
ACTION_THROW: int = pygame.K_t


TARGET_KEY: int = pygame.K_f

PLAYER_ACTIONS: dict[int, str] = {
    ACTION_PICKUP: "pick_up",
    ACTION_EQUIP: "equip",
    ACTION_CAST: "cast",
    ACTION_UPSTAIRS: "upstairs",
    ACTION_DOWNSTAIRS: "downstairs",
    ACTION_TAKE_OFF: "take_off",
    ACTION_DROP: "drop",
    ACTION_QUAFF: "drink",
    ACTION_READ: "read",
    ACTION_CURSOR: "cursor",
    ACTION_STATS: "stats",
    ACTION_FIRE: "fire",
    ACTION_THROW: "throw",
}
