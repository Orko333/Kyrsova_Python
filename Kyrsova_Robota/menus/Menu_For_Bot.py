import random
import pygame
from pygame.locals import *
from Files import Configs
from music_manage import Music_Controller
from games.Fight_With_Bot import SinglePlayerChompGame
from menus.One_On_One_Menu import One_ON_One
from other.Dropspusok import Dropdown, DropdownOption

class Menu_For_Bot(One_ON_One):
    def __init__(self):
        """Ініціалізує меню 'Меню Для Бота' з налаштуваннями складності"""
        super().__init__()

        self.difficulty_options = [
            DropdownOption("Легка", "easy", {
                "EN": "Easy",
                "UA": "Легка"
            }),
            DropdownOption("Середня", "medium", {
                "EN": "Medium",
                "UA": "Середня"
            }),
            DropdownOption("Тяжка", "hard", {
                "EN": "Hard",
                "UA": "Тяжка"
            }),
        ]

        base_x = (self.WINDOW_SIZE[0] - 300) // 2
        base_y = self.get_button_rect(len(self.buttons) - 1).bottom + 50

        self.difficulty_dropdown = Dropdown(
            base_x, base_y + (50 + 40) * 1,
            300, 50,
            self.difficulty_options,
            self.button_font
        )

    def start(self):
        """Оновлює налаштування з випадаючих списків та запускає гру"""
        size_value = self.size_options[self.size_dropdown.selected_option].value
        self.rows, self.cols = size_value

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

        difficulty_value = self.difficulty_options[self.difficulty_dropdown.selected_option].value
        print(f"Selected difficulty: {difficulty_value}")

        game = SinglePlayerChompGame(
            rows=self.rows,
            cols=self.cols,
            poison_pos=self.poison_pos,
            difficulty=difficulty_value
        )
        self.running = False
        game.run()

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
                self.position_dropdown.handle_event(event)
                self.difficulty_dropdown.handle_event(event)

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
                self.get_translation("Плитка смерті"),
                self.get_translation("Складність")
            ]
            for i, label in enumerate(labels):
                label_surface = label_font.render(label, True, self.BUTTON_COLOR)
                label_rect = label_surface.get_rect(
                    bottomleft=(self.size_dropdown.rect.left,
                                [self.size_dropdown.rect.top,
                                 self.position_dropdown.rect.top,
                                 self.difficulty_dropdown.rect.top][i] - 5)
                )
                self.screen.blit(label_surface, label_rect)

            self.size_dropdown.draw(self.screen)
            self.position_dropdown.draw(self.screen)
            self.difficulty_dropdown.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)