import pygame

black = (0, 0, 0)
grey = (160, 160, 160)


def grid(screen, size):
    for y in range(size):
        offset_y = 2 * y
        for x in range(size):
            offset_x = 2 * x
            rect = (x * 54 + offset_x, y * 54 + offset_y, 54, 54)
            pygame.draw.rect(screen, grey, (rect))


def place_image(image, screen, pos):
    y = pos[0] * 54
    offset = 2 * pos[0]
    row = y + offset
    x = pos[1] * 54
    offset = 2 * pos[1]
    column = x + offset
    screen.blit(image, [column, row])
