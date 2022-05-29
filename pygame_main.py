"""Pygame-main

Requires Pygame to be installed"""

try:
    import pygame
except (ImportError, ModuleNotFoundError):
    raise Exception(
        "Pygame is not installed. Install it with pip install pygame") from None

pygame.init()
