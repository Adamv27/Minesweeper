import os
import random
import draw
import time
import pygame
import pygame_gui

pygame.init()
WIDTH = 650
HEIGHT = 500

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))

background = pygame.Surface((WIDTH, HEIGHT))
background.fill((0, 0, 0))

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

new_board_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((525, 175), (100, 50)),
                                                text='New Board',
                                                manager=manager)

reveal_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((525, 250), (100, 50)),
                                             text='Reveal Board',
                                             manager=manager)
clock = pygame.time.Clock()
is_running = True


class GameBoard:
    def __init__(self):
        self.board = [[0 for i in range(9)] for j in range(9)]
        self.uncovered_spaces = []
        self.flags = []

        self.bomb = 'X'
        self.bomb_count = 10

    def print_board(self):
        for row in self.board:
            print(row)

    def reset_board(self):
        # All default (blank) tiles are represented with a 0
        self.board = [[0 for i in range(9)] for j in range(9)]
        self.flags = []
        self.uncovered_spaces = []

    def create_board(self):
        self.reset_board()
        self.add_bombs()
        self.get_adjacent_bomb_count()
        self.print_board()
        print()

    def add_bombs(self):
        available_spots = self.get_board_space_index()
        # 10 total bombs are on the board
        for bomb in range(self.bomb_count):
            random_spot = random.choice(available_spots)
            # A bomb can not be placed on top of another bomb
            available_spots.remove(random_spot)

            y, x = random_spot
            self.board[y][x] = self.bomb

    def get_board_space_index(self):
        # Return a 2d grid of indexes in order to place bombs
        return [[y_index, x_index] for y_index, y in enumerate(self.board) for x_index, x in enumerate(y)]

    def place_flag(self, row, column):
        self.flags.append((row, column))

    def is_win(self):
        bombs = self.get_bomb_location()
        return set(bombs) == set(self.flags)

    def get_bomb_location(self):
        bombs = []
        for row in range(9):
            for column in range(9):
                if self.board[row][column] == 'X':
                    bombs.append((row, column))
        return bombs

    def get_adjacent_bomb_count(self):
        bomb_count = 0
        for row, y in enumerate(self.board):
            for column, x in enumerate(y):
                if self.board[row][column] != self.bomb:
                    # Check the neighboring tiles to see if it is a bomb space
                    for adjacent_tiles in [0, 1], [1, 0], [1, 1], [0, -1], [-1, 0], [-1, -1], [1, -1], [-1, 1]:
                        adj_x, adj_y = adjacent_tiles
                        # The space being checked must be inside the grid's bounds
                        if 8 >= column + adj_x >= 0 and 8 >= row + adj_y >= 0:
                            if self.board[row + adj_y][column + adj_x] == self.bomb:
                                bomb_count += 1
                                # Increase the count of the tile meaning it is touching a bomb
                                self.board[row][column] += 1


class Uncover:
    def __init__(self, board):
        self.uncovered = []
        self.checked = []
        self.board = board

    def uncover(self, pos):
        self.find_adj_empty_spaces(pos)
        return self.uncovered

    def find_adj_empty_spaces(self, pos):
        row, column = pos
        for adjacent_tiles in [0, 1], [1, 0], [0, -1], [-1, 0]:
            adj_x, adj_y = adjacent_tiles
            new_pos = [row + adj_y, column + adj_x]
            if 8 >= column + adj_x >= 0 and 8 >= row + adj_y >= 0 and new_pos not in self.checked:
                if self.board[row + adj_y][column + adj_x] == 0:
                    self.uncovered.append(new_pos)
                    self.checked.append(new_pos)
                    self.find_adj_empty_spaces(new_pos)
                else:
                    self.checked.append(new_pos)


class Graphics:
    def __init__(self, surface):
        self.surface = surface
        self.board = board.board

        # holds spaces that have been clicked on (row, column)
        self.uncovered_spaces = []
        self.flags = []
        self.images = {}
        self.load_images()

    def load_images(self):
        os.chdir('graphics')
        for file in os.listdir():
            image = pygame.image.load(file)
            image = pygame.transform.scale(image, (54, 54))
            self.images[file[:-4]] = image

    def reset(self):
        self.uncovered_spaces = []
        self.flags = []
        self.board = board.board
        self.render()

    def reveal(self):
        for row in range(9):
            for column in range(9):
                self.uncovered_spaces.append((row, column))

    def win(self):
        font = pygame.font.SysFont('arial', 100)
        self.surface.fill((255,255,255))
        text_surf = font.render('You Won!', True, (0, 255, 255), )
        self.surface.blit(text_surf, (100, 175))

    def game_over(self):
        font = pygame.font.SysFont('arial', 100)
        self.surface.fill((255, 255, 255))
        text_surf = font.render('Game Over!', True, (255, 0, 0), )
        self.surface.blit(text_surf, (50, 175))

    def render(self):
        for space in self.uncovered_spaces:
            row = space[0]
            column = space[1]
            if self.board[row][column] == 'X':
                image = self.images['bomb']
                pos = (row, column)
                draw.place_image(image, self.surface, pos)
            elif self.board[row][column] in list(range(1, 9)):
                image = self.images[str(self.board[row][column])]
                pos = (row, column)
                draw.place_image(image, self.surface, pos)

        for row, y in enumerate(self.board):
            for column, x in enumerate(y):
                if (row, column) not in self.uncovered_spaces:
                    image = self.images['tile']
                    pos = (row, column)
                    draw.place_image(image, self.surface, pos)
                if (row, column) in self.flags:
                    image = self.images['flag']
                    pos = (row, column)
                    draw.place_image(image, self.surface, pos)


def click_in_board(pos):
    x = pos[0]
    y = pos[1]
    return (0 <= x <= 500) and (0 <= y <= 500)


def get_index(pos):
    x = pos[0]
    y = pos[1]
    x_offset = (x // 54) * 2
    y_offset = (y // 54) * 2
    x -= x_offset
    y -= y_offset
    return y // 54, x // 54


def game_over():
    board.create_board()
    graphics.reset()


board = GameBoard()
board.create_board()

graphics = Graphics(window_surface)

game_is_over = False
clicked_on_bomb = False

while is_running:
    while not game_is_over:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == new_board_button:
                        board.create_board()
                        graphics.reset()
                    elif event.ui_element == reveal_button:
                        graphics.reveal()
                        game_is_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left click to uncover tiles
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if click_in_board(pos):
                        row, column = get_index(pos)
                        if board.board[row][column] != 0:
                            graphics.uncovered_spaces.append((row, column))
                            board.uncovered_spaces.append((row, column))
                            if board.board[row][column] == 'X':
                                graphics.game_over()
                                clicked_on_bomb = True
                        else:
                            uncover = Uncover(board.board)
                            empty_spaces = uncover.uncover([row, column])
                            if len(empty_spaces) > 1:
                                for space in empty_spaces:
                                    graphics.uncovered_spaces.append((space[0], space[1]))
                                    board.uncovered_spaces.append((row, column))
                            else:
                                graphics.uncovered_spaces.append((row, column))
                                board.uncovered_spaces.append((row, column))
                # Right click to place flag
                elif event.button == 3:
                    row, column = get_index(pygame.mouse.get_pos())
                    if (row, column) in board.uncovered_spaces:
                        print('uncovered')
                    else:
                        if (row, column) not in board.flags:
                            board.place_flag(row, column)
                            graphics.flags.append((row, column))
                        else:
                            board.flags.remove((row, column))
                            graphics.flags.remove((row, column))

            manager.process_events(event)
        manager.update(time_delta)
        window_surface.blit(background, (0, 0))
        draw.grid(window_surface, 9)
        graphics.render()

        if board.is_win():
            pygame.display.update()
            graphics.win()
            game_is_over = True
        elif clicked_on_bomb:
            pygame.display.update()
            graphics.game_over()
            game_is_over = True

        manager.draw_ui(window_surface)
        pygame.display.update()

    time.sleep(2)
    game_over()
    game_is_over = False
    clicked_on_bomb = False
