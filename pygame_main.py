"""Pygame-main

Requires Pygame to be installed"""

import math
from os import remove
from typing import Union
from time import sleep
from socket import socket, AF_UNIX, SOCK_STREAM
try:
    import pygame
    from pygame.locals import *
except (ImportError, ModuleNotFoundError):
    raise Exception(
        "Pygame is not installed. Install it with pip install pygame") from None


main_sock = socket(AF_UNIX, SOCK_STREAM)
try:
    main_sock.bind("/tmp/pygame_main.sock")
except Exception:
    remove("/tmp/pygame_main.sock")
    main_sock.bind("/tmp/pygame_main.sock")
main_sock.listen()
sock = main_sock.accept()[0]
print("Connected to socket")
sock.send(b"Hello!\n")
pygame.init()
screen = pygame.display.set_mode((500, 500), 0, 0, 0, 1)
isfullscreen = False
running = True
rect = pygame.Rect(250, 250, 20.0, 20.0)
player_pos = [250, 250, 20, 20]
width, height = screen.get_width(), screen.get_height()
pygame.key.set_repeat(500, 30)
max_bull = 50
clock = pygame.time.Clock()

bulpos = []
bulconf = (2,2)
bull: list[pygame.Rect] = []

RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
delay = 50

while running is True:
    width, height = screen.get_size()
    mpos = pygame.mouse.get_pos()
    angle = math.atan2(
        mpos[1] - (player_pos[1] + 32), mpos[0] - (player_pos[0] + 26))
    while delay != 0:
        delay -= 1
    else:
        screen.unlock()
            
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            pygame.quit()
            break
        if event.type == KEYDOWN:
            hold = True
            #print(f"\r\033[2K\r{event.type = } | {event.key = } | {player_pos = }", end="")
            if event.key == K_BACKSPACE:
                running = False
                pygame.quit()
            if event.key == K_1:
                if screen.get_locked() is False:
                    isfullscreen = pygame.display.toggle_fullscreen()
                    delay = 20
                    screen.lock()
            if event.key == K_UP:
                if player_pos[1] > 0:
                    player_pos[1] -= 5
            elif event.key == K_DOWN:
                if player_pos[1] < (height-player_pos[-1]):
                    player_pos[1] += 5
            elif event.key == K_LEFT:
                if player_pos[0] > 0:
                    player_pos[0] -= 5
            elif event.key == K_RIGHT:
                if player_pos[0] < (width-player_pos[-2]):
                    player_pos[0] += 5
            elif event.key == K_q:
                if len(bull) < max_bull:
                    bull.append((pygame.Rect(rect.midtop[0], player_pos[1]+1, 4, 4), angle))
            elif event.key == K_z:
                bull.clear()
            elif event.key == K_x:
                player_pos[0] = 250
                player_pos[1] = 250
            elif event.key == K_c:
                max_bull += 10
            elif event.key == K_v:
                max_bull -= 10
            elif event.key == K_TAB:
                if delay == 0:
                    delay = 20
                    sleep(2)
        if event.type == KEYUP:
            hold = False
            hold_key = None
        #print(f"\r\033[2K\r{event.type = } | {hold = } | {time() = }", end="")

        """if hold is True:
            if hold_key == "up":
                if player_pos[1] > 0:
                    player_pos[1] -= 5
            elif hold_key == "down":
                if player_pos[1] < (height-100):
                    player_pos[1] += 5  # add y
            elif hold_key == "left":
                if player_pos[0] > 0:
                    player_pos[0] -= 5
            elif hold_key == "right":
                if player_pos[0] < (width-100):
                    player_pos[0] += 5"""

    if running is False:
        break

    print(f"\r\033[2K\r{player_pos[:2] = } | bullets = {len(bull)}/{max_bull} | FPS = {clock.get_fps():2.0f} | MPOS = {mpos}", end="")
    try:
        sock.send(
            f"\r\033[2K{player_pos[:2] = } | bullets = {len(bull)}/{max_bull} | FPS = {clock.get_fps():2.0f} | MPOS + {mpos}".encode())
    except BrokenPipeError:
        try:
            sock.close()
        except Exception:
            pass
        pygame.quit()
        break
    screen.fill(GRAY)
    rect = Rect(*player_pos)
    pygame.draw.rect(screen, RED, rect, 4)
    for b in bull.copy():
        d: pygame.Rect = b[0]
        vel_x = math.cos(b[-1]) * 10
        vel_y = math.sin(b[-1]) * 10
        d.update(d.left+vel_x, d.top+vel_y, 4, 4)
        p = d.top, d.bottom, d.left, d.right
        pygame.draw.rect(screen, (0, 0, 0), d, 4)
        if p[1] <= 0 or p[1] >= height+1 or p[0] <= 0 or p[0] >= width+1:
            bull.remove(b)
    pygame.display.flip()
    clock.tick(60)
print(" "*30)
sock.send(b">>Request close")
try:
    sock.close()
except Exception:
    pass
remove("/tmp/pygame_main.sock")