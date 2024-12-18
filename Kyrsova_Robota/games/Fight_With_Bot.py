import math
import random

import pygame
from pygame.locals import *

from Files import Configs
from games.User_Interface import GameUI
from botu.Bots import ChompBot
from games.Game import ChompGame


class SinglePlayerChompGame(ChompGame):
    """
    Клас для гри Chomp з одним гравцем проти бота з підтримкою складності.
    """

    def __init__(self, rows=3, cols=4, time_limit=None, poison_pos=(0, 0), bot=None, difficulty='easy'):
        """
        Ініціалізація гри Chomp з одним гравцем проти бота.

        :param rows: кількість рядків на дошці
        :param cols: кількість стовпців на дошці
        :param time_limit: обмеження часу для кожного гравця
        :param poison_pos: позиція отруєного блоку
        :param bot: об'єкт бота
        :param difficulty: рівень складності бота
        """
        super().__init__(rows, cols, time_limit, poison_pos)
        self.ui = GameUI(self.WINDOW_SIZE, player1_name="Гравець", player2_name="Бот", language=Configs.current_language)
        self.bot = bot if bot else ChompBot(difficulty)
        self.current_player = 1  # Починає гравець
        self.bot_move_thread = None
        self.bot_move = None
        self.difficulty = difficulty
        self.time_since_player_move = 0

    def get_bot_move(self):
        """
        Отримує хід від бота.
        """
        self.bot_move = self.bot.get_move(self.board, self.poison_pos)

    def check_for_bot_move(self):
        # Перевіряємо, чи пройшов потрібний час
        if self.time_since_player_move >= 2.0:  # Обрати потрібний час затримки (наприклад, 2 секунди)
            self.time_since_player_move = 0  # Скидаємо таймер
            return True
        else:
            return False

    def run(self):
        """
        Запускає головний цикл гри проти бота.
        """
        clock = pygame.time.Clock()
        self.soundmanager.stop_sound("Fonova_Myzuka")
        self.soundmanager.play_sound('Fight_Music', loops=-1, volume=Configs.volume * 0.1)

        while self.running:
            self.time += 1
            self.time_since_player_move += 1 / 60.0

            if self.games_is_started == 1 and self.winner is None:
                if self.current_player == 2:
                    if self.check_for_bot_move():
                        if self.bot_move_thread is None:
                            self.bot_move_thread = self.get_bot_move()

                    if self.bot_move is not None:
                        row, col = self.bot_move
                        if self.board[row][col]:
                            self.soundmanager.play_sound('Lamanie', volume=Configs.volume)
                            if self.eat_chocolate(row, col):
                                if self.winner is None:
                                    self.current_player = 1

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif self.first_time:
                        self.first_time = False
                elif event.type == MOUSEBUTTONDOWN:
                    if self.first_time:
                        self.first_time = False
                    elif self.winner is None and self.current_player == 1:
                        pos = self.get_block_at_pos(pygame.mouse.get_pos())
                        if pos:
                            row, col = map(int, pos)
                            if self.board[row][col]:
                                self.soundmanager.play_sound('Lamanie', volume=Configs.volume)
                                if self.eat_chocolate(row, col):
                                    if self.winner is None:
                                        self.current_player = 2
                                        self.time_since_player_move = 0

                elif event.type == VIDEORESIZE and not Configs.fullscreen:
                    self.WINDOW_SIZE = (event.w, event.h)
                    self.screen = pygame.display.set_mode(self.WINDOW_SIZE, pygame.RESIZABLE)
                    self.calculate_block_size()
                    self.ui = GameUI(self.WINDOW_SIZE, language=Configs.current_language)
                    self.stars = [(random.randint(0, self.WINDOW_SIZE[0]), random.randint(0, self.WINDOW_SIZE[1]),
                                   random.random(), random.random() * 2 * math.pi) for _ in range(150)]

            self.draw_board()
            self.games_is_started = 1
            if self.winner:
                self.ui.draw_game_over(self.screen, self.winner)
                if pygame.key.get_pressed()[pygame.K_r]:
                    self.__init__(self.rows, self.cols, self.time_limit, self.poison_pos, difficulty=self.difficulty)
            pygame.display.flip()
            clock.tick(60)

        self.running = False
        return self.winner