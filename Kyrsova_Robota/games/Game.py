import pygame
from pygame.locals import *

from Files import Configs
import random
import math
from Blocks_and_textures.Chastunku import Particle
from Blocks_and_textures.Blocks import AnimatedBlock
from games.User_Interface import GameUI
from music_manage import Music_Controller

class ChompGame:
    """
    Клас для гри Chomp.
    """

    def __init__(self, rows=3, cols=4, time_limit=None, poison_pos=(0, 0)):
        """
        Ініціалізація гри Chomp.

        :param rows: кількість рядків на дошці
        :param cols: кількість стовпців на дошці
        :param time_limit: обмеження часу для кожного гравця
        :param poison_pos: позиція отруєного блоку
        """
        pygame.init()
        self.WINDOW_SIZE = {0: (720, 480), 1: (1280, 720), 2: (1920, 1080)}.get(Configs.resolution_index)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE, pygame.FULLSCREEN if Configs.fullscreen else pygame.RESIZABLE)
        pygame.display.set_caption("CHOMP!")

        # Налаштування гри
        self.rows, self.cols, self.time_limit, self.poison_pos = rows, cols, time_limit, poison_pos
        self.current_player, self.running, self.winner, self.time = 1, True, None, 0
        self.time_left_player1 = self.time_left_player2 = time_limit
        self.last_time_player1 = self.last_time_player2 = pygame.time.get_ticks()

        # Ініціалізація UI
        self.ui = GameUI(self.WINDOW_SIZE, language=Configs.current_language)
        self.first_time = True  # Для накладання підказок

        # Налаштування дошки
        self.board = [[True for _ in range(cols)] for _ in range(rows)]
        self.animated_blocks = []
        self.games_is_started = 0

        # Кольори
        self.CHOCOLATE_COLOR = (139, 69, 19)
        self.POISON_COLOR = (178, 34, 34)
        self.PLAYER1_COLOR = (46, 139, 87)
        self.PLAYER2_COLOR = (70, 130, 180)
        self.GRADIENT_TOP = (0, 0, 0)
        self.GRADIENT_BOTTOM = (172, 16, 0)

        # Розрахунок розміру блоків
        self.calculate_block_size()

        # Налаштування шрифтів
        self.font = pygame.font.Font(None, int(self.WINDOW_SIZE[1] * 0.05))

        # Система частинок
        self.particles = []

        # Фон зі зірками
        self.stars = [(random.randint(0, self.WINDOW_SIZE[0]), random.randint(0, self.WINDOW_SIZE[1]), random.random(), random.random() * 2 * math.pi) for _ in range(150)]

        # Висота блоків
        self.block_height = self.block_size * 0.15

        # Налаштування звуку
        self.soundmanager = Music_Controller.sound_manager

    def calculate_block_size(self):
        """
        Розраховує розмір блоків на дошці.
        """
        max_width, max_height = self.WINDOW_SIZE[0] * 0.65, self.WINDOW_SIZE[1] * 0.65
        self.block_size = min(max_width // (self.cols + 1), max_height // (self.rows + 1)) * 1.2
        self.board_x = (self.WINDOW_SIZE[0] - (self.cols * self.block_size)) // 2
        self.board_y = (self.WINDOW_SIZE[1] - (self.rows * self.block_size)) // 2

    def create_particles(self, x, y, color, amount=20):
        """
        Створює частинки для анімації.

        :param x: координата x
        :param y: координата y
        :param color: колір частинок
        :param amount: кількість частинок
        """
        for _ in range(amount):
            speed, size = random.uniform(3, 7), random.uniform(3, 8)
            self.particles.append(Particle(x + random.uniform(-15, 15), y + random.uniform(-15, 15), color, size, speed))

    def draw_gradient_background(self):
        """
        Малює градієнтний фон.
        """
        height = self.WINDOW_SIZE[1]
        for y in range(height):
            ratio = y / height
            color = [self.GRADIENT_TOP[i] * (1 - ratio / 0.3) + self.GRADIENT_BOTTOM[i] * (ratio / 0.3) for i in range(3)] if ratio < 0.3 else self.GRADIENT_BOTTOM
            flicker = math.sin(y * 0.1 + self.time * 0.01) * 5
            color = [max(0, min(255, c + flicker)) for c in color]
            pygame.draw.line(self.screen, color, (0, y), (self.WINDOW_SIZE[0], y))

    def draw_stars(self):
        """
        Малює зірки на фоні.
        """
        for i, (x, y, brightness, phase) in enumerate(self.stars):
            current_brightness = brightness * (0.6 + 0.4 * math.sin(self.time * 0.03 + phase))
            size = 1 + brightness * 2
            color = (255, 255, 255, int(current_brightness * 255))
            surf = pygame.Surface((int(size * 3), int(size * 3)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color[:3], 50), (size * 1.5, size * 1.5), size * 1.5)
            pygame.draw.circle(surf, color, (size * 1.5, size * 1.5), size)
            self.screen.blit(surf, (int(x - size * 1.5), int(y - size * 1.5)))
            new_x = (x + brightness * 0.2) % self.WINDOW_SIZE[0]
            self.stars[i] = (new_x, y, brightness, phase)

    def draw_board(self):
        """
        Малює ігрову дошку.
        """
        self.draw_gradient_background()
        self.draw_stars()
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            p.draw(self.screen)
        self.animated_blocks = [block for block in self.animated_blocks if block.update()]
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col]:
                    x, y = self.board_x + col * self.block_size, self.board_y + row * self.block_size
                    poison = (row, col) == self.poison_pos
                    block = AnimatedBlock(x, y, poison, self.block_size, self.block_height)
                    block.draw(self.screen)
        for block in self.animated_blocks:
            block.draw(self.screen)
        mouse_pos = pygame.mouse.get_pos()
        hovered_block = self.get_block_at_pos(mouse_pos)
        if hovered_block:
            row, col = map(int, hovered_block)
            if self.board[row][col]:
                x, y = self.board_x + col * self.block_size, self.board_y + row * self.block_size
                self.ui.draw_hover_effect(self.screen, (x, y), self.block_size)
        self.ui.draw_player_info(self.screen, self.current_player, self.time_left_player1 if self.current_player == 1 else self.time_left_player2)
        if self.first_time:
            self.ui.draw_tutorial_overlay(self.screen, True)

    def eat_chocolate(self, row, col):
        """
        Обробляє з'їдання шоколадки.

        :param row: рядок блоку
        :param col: стовпець блоку
        :return: True, якщо шоколадка з'їдена, False в іншому випадку
        """
        if not self.board[row][col]:
            return False

        if row < self.poison_pos[0]:  # Натискання вище отруйного блоку
            for i in range(row + 1):
                for j in range(self.cols):
                    self.remove_block(i, j)

        elif row > self.poison_pos[0]:  # Натискання нижче отруйного блоку
            for i in range(row, self.rows):
                for j in range(self.cols):
                    self.remove_block(i, j)

        elif col < self.poison_pos[1]:  # Натискання зліва від отруйного блоку
            for i in range(self.rows):
                for j in range(col + 1):
                    self.remove_block(i, j)

        elif col > self.poison_pos[1]:  # Натискання справа від отруйного блоку
            for i in range(self.rows):
                for j in range(col, self.cols):
                    self.remove_block(i, j)

        if (row, col) == self.poison_pos:
            if self.ui.player2_name == "Бот" and self.current_player == 2:
                self.soundmanager.play_sound("You_Win", volume=Configs.volume)
            else:
                self.soundmanager.play_sound("You_Lose", volume=Configs.volume)
            self.winner = 3 - self.current_player
            return True

        return True

    def remove_block(self, row, col):
        """
        Видаляє блок з дошки.

        :param row: рядок блоку
        :param col: стовпець блоку
        """
        if self.board[row][col]:
            self.board[row][col] = False
            x, y = self.board_x + col * self.block_size, self.board_y + row * self.block_size
            poison = (row, col) == self.poison_pos
            color = self.POISON_COLOR if poison else self.CHOCOLATE_COLOR
            block = AnimatedBlock(x, y, poison, self.block_size, self.block_height)
            block.falling = True
            block.fall_speed = random.uniform(-2, 2)
            self.animated_blocks.append(block)
            self.create_particles(x + self.block_size // 2, y + self.block_size // 2, color, 20)

    def get_block_at_pos(self, pos):
        """
        Повертає блок за вказаною позицією миші.

        :param pos: позиція миші
        :return: координати блоку або None
        """
        x, y = pos
        adjusted_x, adjusted_y = x - self.board_x - self.block_height, y - self.board_y + self.block_height
        board_x, board_y = adjusted_x // self.block_size, adjusted_y // self.block_size
        if 0 <= board_x < self.cols and 0 <= board_y < self.rows and self.board_x <= x < self.board_x + self.cols * self.block_size and self.board_y <= y < self.board_y + self.rows * self.block_size:
            return board_y, board_x
        return None

    def run(self):
        """
        Запускає головний цикл гри.
        """
        clock = pygame.time.Clock()
        self.soundmanager.stop_sound("Fonova_Myzuka")
        self.soundmanager.play_sound('Fight_Music', loops=-1, volume=Configs.volume * 0.1)
        while self.running:
            self.time += 1
            if self.games_is_started == 1 and self.winner is None:
                self.update_timer()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.soundmanager.stop_sound("Fight_Music")
                    self.soundmanager.play_sound("Fonova_Myzuka", loops=-1, volume=Configs.volume * 0.2)
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.soundmanager.stop_sound("Fight_Music")
                        self.soundmanager.play_sound("Fonova_Myzuka", loops=-1, volume=Configs.volume * 0.2)
                        self.running = False
                    elif self.first_time:
                        self.first_time = False
                elif event.type == MOUSEBUTTONDOWN:
                    if self.first_time:
                        self.first_time = False
                    elif self.winner is None:
                        pos = self.get_block_at_pos(pygame.mouse.get_pos())
                        if pos:
                            row, col = map(int, pos)
                            if self.board[row][col]:
                                self.soundmanager.play_sound('Lamanie', volume=Configs.volume)
                                if self.eat_chocolate(row, col):
                                    if self.winner is None:
                                        self.current_player = 3 - self.current_player
                                        self.update_timer()
                                        self.drop_timer()
                elif event.type == VIDEORESIZE and not Configs.fullscreen:
                    self.WINDOW_SIZE = (event.w, event.h)
                    self.screen = pygame.display.set_mode(self.WINDOW_SIZE, pygame.RESIZABLE)
                    self.calculate_block_size()
                    self.ui = GameUI(self.WINDOW_SIZE, language=Configs.current_language)
                    self.stars = [(random.randint(0, self.WINDOW_SIZE[0]), random.randint(0, self.WINDOW_SIZE[1]), random.random(), random.random() * 2 * math.pi) for _ in range(150)]
            self.draw_board()
            self.games_is_started = 1
            if self.winner:
                self.ui.draw_game_over(self.screen, self.winner)
                if pygame.key.get_pressed()[pygame.K_r]:
                    self.__init__(self.rows, self.cols, self.time_limit, self.poison_pos)
            pygame.display.flip()
            clock.tick(60)
        self.running = False
        return self.winner

    def drop_timer(self):
        """
        Скидає таймер для обох гравців.
        """
        self.time_left_player1 = self.time_left_player2 = self.time_limit

    def update_timer(self):
        """
        Оновлює таймер для поточного гравця.
        """
        current_time = pygame.time.get_ticks()
        if self.current_player == 1 and self.time_left_player1 is not None:
            if current_time - self.last_time_player1 >= 1000:
                self.time_left_player1 -= 1
                self.last_time_player1 = current_time
                if self.time_left_player1 <= 0:
                    self.soundmanager.play_sound("You_Lose", volume=Configs.volume)
                    self.winner = 2
        elif self.current_player == 2 and self.time_left_player2 is not None:
            if current_time - self.last_time_player2 >= 1000:
                self.time_left_player2 -= 1
                self.last_time_player2 = current_time
                if self.time_left_player2 <= 0:
                    self.soundmanager.play_sound("You_Lose", volume=Configs.volume)
                    self.winner = 1