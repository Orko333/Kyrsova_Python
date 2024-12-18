from Files.Work_With_File import *
from menus.Menu_Class import Menu
from Files import Configs


class SettingsMenu(Menu):
    def __init__(self):
        super().__init__("Налаштування")

        self.buttons = [
            ("Змінити мову", self.change_language),
            ("Повернутися", self.back_to_main_menu),
        ]
        # Доступні роздільні здатності
        self.resolutions = [
            (720,480),
            (1280, 720),
            (1920, 1080),
        ]

        self.buttons = [
            ("Роздільна здатність", self.change_resolution),
            ("Гучність", self.change_volume),
            ("Повноекранний режим", self.toggle_fullscreen_setting),
            ("Змінити мову", self.change_language),
            ("Повернутися", self.back_to_main_menu),
        ]
        self.setup_buttons()

    def draw_settings_values(self):
        """Відображає поточні значення налаштувань біля кнопок"""
        for i, (text, _) in enumerate(self.buttons):
            button_rect = self.get_button_rect(i)
            value_text = ""

            if text == "Роздільна здатність" or text == "Resolution":
                current_res = self.resolutions[Configs.resolution_index]
                value_text = f"{current_res[0]}x{current_res[1]}"
            elif text == "Гучність" or text == "Volume":
                value_text = f"{int(Configs.volume * 100)}%"
            elif text == "Повноекранний режим" or text == "Fullscreen":
                value_text = "✓" if self.fullscreen else "×"

            if value_text:
                value_surface = self.button_font.render(value_text, True, self.TEXT_COLOR)
                value_rect = value_surface.get_rect(
                    midleft=(button_rect.right + 20, button_rect.centery)
                )
                self.screen.blit(value_surface, value_rect)

    def change_resolution(self):
        """Змінює роздільну здатність циклічно"""
        new_resolution_index = (Configs.resolution_index + 1) % len(self.resolutions)
        Configs.resolution_index = new_resolution_index

    def change_volume(self):
        """Змінює гучність циклічно (0.2 -> 0.4 -> 0.6 -> 0.8 -> 1.0 -> 0.2)"""
        Configs.volume = round((Configs.volume + 0.2) % 1.2, 1)

    def toggle_fullscreen_setting(self):
        Configs.fullscreen = 1 if Configs.fullscreen == 0 else 0

    def back_to_main_menu(self):
        """Callback для повернення до головного меню"""
        file_write()
        self.running = False

    def add_something_previous_quit(self):
        file_write()

    def change_language(self):
        """Змінює мову циклічно"""
        Configs.current_language = "EN" if Configs.current_language == "UA" else "UA"
        self.setup_buttons()

    def add_something_to_run(self):
        """Додаткова функція для відображення значень налаштувань"""
        self.draw_settings_values()