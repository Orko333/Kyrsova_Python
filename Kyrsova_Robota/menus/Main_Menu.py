import sys
from Blocks_and_textures.Chastunku import *
from menus.Fight_Menu import Fight_menu
from menus.Settings_Menu import *
from menus.Menu_Class import Menu
from music_manage import Music_Controller


class MainMenu(Menu):
    def __init__(self):
        super().__init__("CHOMP!")
        self.buttons = [
            ("Грати", self.start_game),
            ("Налаштування", self.settings),
            ("Вийти", self.quit_game)
        ]
        self.setup_buttons()
        self.music=Music_Controller.sound_manager.play_sound("Fonova_Myzuka", loops=-1, volume=0.2 * Configs.volume)

    def draw_made_by_text(self):
        """Малює надпис 'MADE BY ORKO' з ефектом світіння та райдужним кольором"""
        made_by_text = "MADE BY ORKO"
        bottomright = (self.WINDOW_SIZE[0] - 20, self.WINDOW_SIZE[1] - 20)

        # Створюємо кілька шарів тексту для світіння
        for offset in range(10, 0, -1):
            glow_surface = self.made_by_font.render(made_by_text, True, (*self.TITLE_COLOR[:3], 20 // offset))
            glow_rect = glow_surface.get_rect(bottomright=bottomright)
            glow_rect.inflate_ip(offset * 2, offset * 2)
            self.screen.blit(glow_surface, glow_rect)

        # Основний текст з райдужним ефектом
        hue = (self.time * 0.5) % 360
        made_by_color = pygame.Color(0, 0, 0)
        made_by_color.hsva = (hue, 30, 100, 100)

        # Малюємо тінь тексту
        for shift_x, shift_y in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            shadow_surface = self.made_by_font.render(made_by_text, True, (0, 0, 0, 100))
            shadow_rect = shadow_surface.get_rect(bottomright=(bottomright[0] + shift_x, bottomright[1] + shift_y))
            self.screen.blit(shadow_surface, shadow_rect)

        # Основний кольоровий текст
        made_by_surface = self.made_by_font.render(made_by_text, True, made_by_color)
        made_by_rect = made_by_surface.get_rect(bottomright=bottomright)
        self.screen.blit(made_by_surface, made_by_rect)

    def add_something_to_run(self):
        """Додає функцію для малювання надпису 'MADE BY ORKO' до основного циклу"""
        self.draw_made_by_text()

    def start_game(self):
        """Callback для початку гри"""
        fight_menu = Fight_menu()
        fight_menu.run()

    def settings(self):
        """Callback для переходу до налаштувань"""
        settings_menu = SettingsMenu()
        settings_menu.run()
        self.perebydova = 1
        self.running = 0

    def quit_game(self):
        """Callback для виходу з гри"""
        pygame.quit()
        sys.exit()