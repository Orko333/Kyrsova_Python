import pygame
from Files import Configs
from Files.Work_With_File import file_read_U, file_read_E


class DropdownOption:
    def __init__(self, text, value, translations=None):
        """
        Ініціалізує об'єкт опції випадаючого списку.

        :param text: Текст опції.
        :param value: Значення опції.
        :param translations: Словник перекладів (необов'язково).
        """
        self.original_text = text
        self.translations = translations or {}
        self.value = value
        self.hover_scale = 1.0
        self.particles = []

    def get_translation(self):
        """
        Отримує переклад тексту відповідно до поточної мови.

        :return: Перекладений або оригінальний текст.
        """
        translations = {
            "UA": file_read_U(),
            "EN": file_read_E()
        }
        current_lang = Configs.current_language

        # Спочатку перевіряємо власні переклади
        if current_lang in self.translations:
            return self.translations[current_lang]

        # Потім перевіряємо загальні файли перекладів
        return translations.get(current_lang, {}).get(self.original_text, self.original_text)

    @property
    def text(self):
        """
        Повертає поточний текст з перекладом.

        :return: Текст поточною мовою.
        """
        return self.get_translation()


class Dropdown:
    active_dropdown = None  # Класовий атрибут для відстеження активного випадаючого списку.

    def __init__(self, x, y, width, height, options, font, initial_option=0, cooficient=1.0):
        """
        Ініціалізує об'єкт випадаючого списку.

        :param x: Координата X для розташування випадаючого списку.
        :param y: Координата Y для розташування випадаючого списку.
        :param width: Ширина випадаючого списку.
        :param height: Висота випадаючого списку.
        :param options: Список опцій для випадаючого списку.
        :param font: Шрифт для тексту опцій.
        :param initial_option: Індекс початкової обраної опції.
        :param cooficient: Коефіцієнт для масштабування елементів.
        """
        self.screen = None
        self.rect = pygame.Rect(x, y, width, height)

        # Перевірка, чи є опції вже екземплярами DropdownOption
        self.options = [opt if isinstance(opt, DropdownOption) else DropdownOption(opt.text, opt.value) for opt in
                        options]

        self.font = font
        self.is_active = False
        self.selected_option = initial_option
        self.option_height = height
        self.cooficient = cooficient
        self.time = 0
        self.hover_index = -1
        self.particles = []
        self.animation_progress = 0

        # Параметри для випадаючого списку, що з'являється праворуч
        self.dropdown_x = self.rect.right + 20
        self.dropdown_width = width

        # Кольори та стилі
        self.BUTTON_COLOR = (255, 255, 255)
        self.BUTTON_SHADOW = (43, 43, 43)
        self.BUTTON_HOVER = (10, 10, 10)
        self.BUTTON_PRESSED = (10, 10, 10)
        self.TEXT_COLOR = (48, 57, 56)
        self.BORDER_COLOR = (255, 215, 0)
        self.BORDER_WIDTH = int(15 * self.cooficient)
        self.text_pressed_color = (255, 215, 0)
        self.text_hover_color = (255, 255, 255)

        # Параметри анімації
        self.button_scale = 1.0
        self.option_scales = [1.0] * len(options)
        self.shadow_offset = int(4 * self.cooficient)

    def draw_button_with_effects(self, screen, rect, text, state="normal", scale=1.0):
        """
        Малює кнопку з ефектами.

        :param screen: Поверхня для малювання.
        :param rect: Прямокутник кнопки.
        :param text: Текст кнопки.
        :param state: Стан кнопки (normal, hover, pressed).
        :param scale: Масштаб кнопки.
        """
        button_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)

        shadow_offset = self.shadow_offset if state != "pressed" else self.shadow_offset // 2
        shadow_rect = pygame.Rect(10, 10 + shadow_offset, rect.width, rect.height)
        pygame.draw.rect(button_surf, self.BUTTON_SHADOW, shadow_rect, border_radius=self.BORDER_WIDTH)

        button_rect = pygame.Rect(10, 10, rect.width, rect.height)
        color = {"normal": self.BUTTON_COLOR, "hover": self.BUTTON_HOVER, "pressed": self.BUTTON_PRESSED}[state]
        pygame.draw.rect(button_surf, color, button_rect, border_radius=self.BORDER_WIDTH)

        highlight_rect = button_rect.copy()
        highlight_rect.height //= 2
        pygame.draw.rect(button_surf, (*[min(255, c + 30) for c in color], 200), highlight_rect, border_radius=self.BORDER_WIDTH)

        if state == "pressed":
            glow_rect = button_rect.copy()
            pygame.draw.rect(button_surf, self.BORDER_COLOR, glow_rect, width=5, border_radius=self.BORDER_WIDTH)

        text_color = {"normal": self.TEXT_COLOR, "hover": self.text_hover_color, "pressed": self.text_pressed_color}[state]
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        button_surf.blit(text_surf, text_rect)

        scaled_size = (int(button_surf.get_width() * scale), int(button_surf.get_height() * scale))
        scaled_surf = pygame.transform.scale(button_surf, scaled_size)
        final_rect = scaled_surf.get_rect(center=rect.center)
        screen.blit(scaled_surf, final_rect)

        if rect.height != self.option_height:
            arrow_points = [(rect.right - 20, rect.centery - 5), (rect.right - 10, rect.centery + 5), (rect.right - 30, rect.centery + 5)]
            if self.is_active:
                arrow_points = [(p[0], rect.centery - (p[1] - rect.centery)) for p in arrow_points]
            pygame.draw.polygon(screen, text_color, arrow_points)

    def draw(self, screen):
        """
        Малює випадаючий список на екрані.

        :param screen: Поверхня для малювання.
        """
        self.time += 1
        main_button_state = "pressed" if self.is_active else "normal"
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            main_button_state = "hover"

        self.draw_button_with_effects(screen, self.rect, self.options[self.selected_option].text, main_button_state, self.button_scale)

        if self.is_active:
            self.animation_progress = min(1.0, self.animation_progress + 0.2)
        else:
            self.animation_progress = max(0.0, self.animation_progress - 0.2)

        if self.animation_progress > 0:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.dropdown_x, self.rect.y - (len(self.options) - i - 1) * self.option_height, self.dropdown_width, self.option_height)
                option_rect.x = self.rect.right + (option_rect.x - self.rect.right) * self.animation_progress

                state = "normal"
                if i == self.hover_index:
                    state = "hover"
                    self.option_scales[i] = min(1.1, self.option_scales[i] + 0.01)
                elif i == self.selected_option:
                    state = "pressed"
                else:
                    self.option_scales[i] = max(1.0, self.option_scales[i] - 0.01)

                self.draw_button_with_effects(screen, option_rect, option.text, state, self.option_scales[i] * self.animation_progress)

    def handle_event(self, event):
        """
        Обробляє події для випадаючого списку.

        :param event: Подія Pygame.
        :return: Повертає True, якщо подія була оброблена, інакше False.
        """
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(mouse_pos):
                if not self.is_active:
                    if Dropdown.active_dropdown and Dropdown.active_dropdown != self:
                        Dropdown.active_dropdown.is_active = False
                    Dropdown.active_dropdown = self
                    self.is_active = True
                else:
                    self.is_active = False
                    Dropdown.active_dropdown = None
                return True

            elif self.is_active:
                for i, option in enumerate(self.options):
                    if i == self.selected_option:
                        continue

                    option_rect = pygame.Rect(self.dropdown_x, self.rect.y - (len(self.options) - i - 1) * self.option_height, self.dropdown_width, self.option_height)
                    option_rect.x = self.rect.right + (self.dropdown_x - self.rect.right) * self.animation_progress

                    if option_rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        self.is_active = False
                        Dropdown.active_dropdown = None
                        return True

        elif event.type == pygame.MOUSEMOTION:
            self.hover_index = -1
            if self.is_active:
                for i, option in enumerate(self.options):
                    if i == self.selected_option:
                        continue
                    option_rect = pygame.Rect(self.dropdown_x, self.rect.y - (len(self.options) - i - 1) * self.option_height, self.dropdown_width, self.option_height)
                    option_rect.x = self.rect.right + (self.dropdown_x - self.rect.right) * self.animation_progress

                    if option_rect.collidepoint(mouse_pos):
                        self.hover_index = i
                        break

            if self.rect.collidepoint(mouse_pos):
                self.button_scale = min(1.1, self.button_scale + 0.01)
            else:
                self.button_scale = max(1.0, self.button_scale - 0.01)

        return False

    def get_selected_value(self):
        """
        Повертає значення обраної опції.

        :return: Значення обраної опції.
        """
        return self.options[self.selected_option].value