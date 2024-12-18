import random
import pygame
from pygame.locals import *

from Files import Configs
from menus.Menu_Class import Menu
from games.Game import ChompGame
from music_manage import Music_Controller
from other.Dropspusok import Dropdown, DropdownOption

class One_ON_One(Menu):
    def __init__(self):
        """Ініціалізує меню 'Один на один' з налаштуваннями"""
        super().__init__("CHOMP!")
        self.rows = 3
        self.cols = 4
        self.time_limit = None
        self.poison_pos = (0, 0)

        self.size_options = [
            DropdownOption("Випадково", (random.randint(2, 10), random.randint(2, 10)), {
                "EN": "Random",
                "UA": "Випадково"
            }),
            DropdownOption("Маленький", (3, 4), {
                "EN": "Small",
                "UA": "Маленький"
            }),
            DropdownOption("Середній", (7, 8), {
                "EN": "Medium",
                "UA": "Середній"
            }),
            DropdownOption("Великий", (9, 10), {
                "EN": "Large",
                "UA": "Великий"
            }),
        ]

        self.time_options = [
            DropdownOption("Без обмеження", None, {
                "EN": "No limit",
                "UA": "Без обмеження"
            }),
            DropdownOption("2 секунд", 2, {
                "EN": "2 seconds",
                "UA": "2 секунд"
            }),
            DropdownOption("5 секунд", 5, {
                "EN": "5 seconds",
                "UA": "5 секунд"
            }),
            DropdownOption("10 секунд", 10, {
                "EN": "10 seconds",
                "UA": "10 секунд"
            }),
            DropdownOption("15 секунд", 15, {
                "EN": "15 seconds",
                "UA": "15 секунд"
            }),
        ]

        self.position_options = [
            DropdownOption("Зліва зверху", (0, 0), {
                "EN": "Top left",
                "UA": "Зліва зверху"
            }),
            DropdownOption("Справа зверху", "sprava_zverhy", {
                "EN": "Top right",
                "UA": "Справа зверху"
            }),
            DropdownOption("Зліва знизу", "zliva_znuzy", {
                "EN": "Bottom left",
                "UA": "Зліва знизу"
            }),
            DropdownOption("Справа знизу", "sprava_znuzy", {
                "EN": "Bottom right",
                "UA": "Справа знизу"
            }),
            DropdownOption("По центрі", "center", {
                "EN": "Center",
                "UA": "По центрі"
            }),
            DropdownOption("Випадково", "random_position", {
                "EN": "Random",
                "UA": "Випадково"
            }),
        ]

        self.buttons = [
            ("Запуск", self.start),
            ("Назад", self.back)
        ]
        self.setup_buttons()

        dropdown_width = 300
        dropdown_height = 50
        base_x = (self.WINDOW_SIZE[0] - dropdown_width) // 2
        last_button_y = self.get_button_rect(len(self.buttons) - 1).bottom
        base_y = last_button_y + 50

        self.size_dropdown = Dropdown(
            base_x, base_y,
            dropdown_width, dropdown_height,
            self.size_options,
            self.button_font
        )

        self.time_dropdown = Dropdown(
            base_x, base_y + dropdown_height + 40,
            dropdown_width, dropdown_height,
            self.time_options,
            self.button_font
        )

        self.position_dropdown = Dropdown(
            base_x, base_y + (dropdown_height + 40) * 2,
            dropdown_width, dropdown_height,
            self.position_options,
            self.button_font
        )

    def start(self):
        """Оновлює налаштування з випадаючих списків та запускає гру"""
        size_value = self.size_options[self.size_dropdown.selected_option].value
        self.rows, self.cols = size_value

        time_value = self.time_options[self.time_dropdown.selected_option].value
        self.time_limit = time_value

        position_value = self.position_options[self.position_dropdown.selected_option].value

        if position_value == "center":
            self.poison_pos = (self.rows // 2, self.cols // 2)
        elif position_value == "sprava_zverhy":
            self.poison_pos = (0, self.cols - 1)
        elif position_value == "zliva_znuzy":
            self.poison_pos = (self.rows - 1, 0)
        elif position_value == "sprava_znuzy":
            self.poison_pos = (self.rows - 1, self.cols - 1)
        elif position_value == "random_position":
            self.poison_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
        else:
            self.poison_pos = position_value

        game = ChompGame(
            rows=self.rows,
            cols=self.cols,
            time_limit=self.time_limit,
            poison_pos=self.poison_pos
        )
        self.running = False
        game.run()

    def back(self):
        """Повертає до попереднього меню"""
        self.running = False

    def run(self):
        """Основний цикл меню"""
        clock = pygame.time.Clock()
        previous_resolution = Configs.resolution_index
        previous_fullscreen = Configs.fullscreen

        while self.running:
            if (previous_resolution != Configs.resolution_index or
                    previous_fullscreen != Configs.fullscreen):
                self.handle_resolution_change()
                previous_resolution = Configs.resolution_index
                previous_fullscreen = Configs.fullscreen

            self.time += 1
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.add_something_previous_quit()
                    self.running = False
                    quit()

                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        Music_Controller.sound_manager.play_sound("Nazatie_Knopku", volume=Configs.volume)
                        for i, (text, callback) in enumerate(self.buttons):
                            if self.get_button_rect(i).collidepoint(mouse_pos):
                                self.pressed_button = i
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1 and self.pressed_button is not None:
                        if self.get_button_rect(self.pressed_button).collidepoint(mouse_pos):
                            self.buttons[self.pressed_button][1]()
                        self.pressed_button = None

                self.size_dropdown.handle_event(event)
                self.time_dropdown.handle_event(event)
                self.position_dropdown.handle_event(event)

            self.draw_gradient_background()
            self.draw_stars()
            self.draw_title_with_effects()
            self.update_particles()

            for i, (text, _) in enumerate(self.buttons):
                button_rect = self.get_button_rect(i)
                state = "normal"
                if i == self.pressed_button:
                    state = "pressed"
                elif button_rect.collidepoint(mouse_pos):
                    state = "hover"
                self.draw_button_with_effects(text, button_rect, state, i)

            label_font = self.button_font
            # Перекладені назви міток
            labels = [
                self.get_translation("Розмір поля"),
                self.get_translation("Час"),
                self.get_translation("Плитка смерті")
            ]
            for i, label in enumerate(labels):
                label_surface = label_font.render(label, True, self.BUTTON_COLOR)
                label_rect = label_surface.get_rect(
                    bottomleft=(self.size_dropdown.rect.left,
                                [self.size_dropdown.rect.top,
                                 self.time_dropdown.rect.top,
                                 self.position_dropdown.rect.top][i] - 5)
                )
                self.screen.blit(label_surface, label_rect)

            self.size_dropdown.draw(self.screen)
            self.time_dropdown.draw(self.screen)
            self.position_dropdown.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)