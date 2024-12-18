import math
import pygame


class GameUI:
    def __init__(self, screen_size, player1_name="Гравець 1", player2_name="Гравець 2", language="UA"):
        """
        Ініціалізує інтерфейс гри з підтримкою перекладу

        :param screen_size: Розмір екрану
        :param player1_name: Ім'я першого гравця
        :param player2_name: Ім'я другого гравця
        :param language: Мова інтерфейсу (UA/EN)
        """
        self.width, self.height = screen_size
        self.font_large = pygame.font.Font(None, int(screen_size[1] * 0.08))
        self.font_medium = pygame.font.Font(None, int(screen_size[1] * 0.05))
        self.font_small = pygame.font.Font(None, int(screen_size[1] * 0.03))

        # Додаємо підтримку перекладу для імен гравців
        self.player_names = {
            "UA": {
                "player1": "Гравець 1",
                "player2": "Гравець 2"
            },
            "EN": {
                "player1": "Player 1",
                "player2": "Player 2"
            }
        }

        # Підтримка перекладу для тексту гри
        self.translations = {
            "UA": {
                "time": "Час: {}с",
                "restart": "Натисніть R для рестарту або ESC для виходу",
                "tutorial_tips": [
                    "Клікайте на шоколадку щоб поламати її",
                    "Уникайте отруєної шоколадки!",
                    "Слідкуйте за часом",
                    "Натисніть будь-яку клавішу або мишу щоб почати"
                ]
            },
            "EN": {
                "time": "Time: {}s",
                "restart": "Press R to restart or ESC to exit",
                "tutorial_tips": [
                    "Click on chocolate to break it",
                    "Avoid the poison chocolate!",
                    "Watch the time",
                    "Press any key or mouse to start"
                ]
            }
        }

        # Встановлюємо поточну мову
        self.language = language

        # Встановлюємо імена гравців з урахуванням мови
        self.player1_name = self.player_names[self.language]["player1"] if player1_name == "Гравець 1" else player1_name
        self.player2_name = self.player_names[self.language]["player2"] if player2_name == "Гравець 2" else player2_name

    def get_translation(self, key, *args):
        """
        Повертає переклад для заданого ключа

        :param key: Ключ перекладу
        :param args: Додаткові аргументи для форматування
        :return: Перекладений текст
        """
        if key in self.translations[self.language]:
            translation = self.translations[self.language][key]
            return translation.format(*args) if args else translation
        return key

    def draw_player_info(self, surface, current_player, time_left=None):
        player_colors = {
            1: (46, 139, 87),  # Зелений
            2: (70, 130, 180)  # Синій
        }

        glow_intensity = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        color = player_colors[current_player]
        glow_color = tuple(min(255, c + int(50 * glow_intensity)) for c in color)

        player_text = self.player1_name if current_player == 1 else self.player2_name
        shadow = self.font_large.render(player_text, True, (0, 0, 0))
        text = self.font_large.render(player_text, True, glow_color)

        pos_x, pos_y = 50, 30
        surface.blit(shadow, (pos_x + 2, pos_y + 2))
        surface.blit(text, (pos_x, pos_y))

        if time_left is not None:
            time_color = (255, 165, 0) if time_left <= 10 else (255, 255, 255)
            time_text = self.get_translation("time", time_left)
            time_surface = self.font_medium.render(time_text, True, time_color)
            surface.blit(time_surface, (self.width - 200, 30))

    def draw_game_over(self, surface, winner):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        scale = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.1 + 0.9
        winner_text = f"{self.player1_name if winner == 1 else self.player2_name} переміг!"
        text_surface = self.font_large.render(winner_text, True, (255, 255, 255))
        scaled_surface = pygame.transform.scale(
            text_surface,
            (int(text_surface.get_width() * scale),
             int(text_surface.get_height() * scale))
        )

        pos_x = self.width // 2 - scaled_surface.get_width() // 2
        pos_y = self.height // 2 - scaled_surface.get_height() // 2
        surface.blit(scaled_surface, (pos_x, pos_y))

        restart_text = self.get_translation("restart")
        restart_surface = self.font_small.render(restart_text, True, (200, 200, 200))
        restart_pos = (
            self.width // 2 - restart_surface.get_width() // 2,
            pos_y + scaled_surface.get_height() + 20
        )
        surface.blit(restart_surface, restart_pos)

    def draw_hover_effect(self, surface, pos, block_size):
        """Малює ефект наведення на блок"""
        x, y = pos
        size = block_size + 4  # Трохи більший розмір для ефекту

        # Анімована рамка
        t = pygame.time.get_ticks() * 0.005
        alpha = int((math.sin(t) + 1) * 127)
        border_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (255, 255, 255, alpha),
                         (0, 0, size, size), 2)

        surface.blit(border_surface,
                     (x - 2, y - 2),
                     special_flags=pygame.BLEND_ADD)

    def draw_tutorial_overlay(self, surface, first_time=False):
        """Малює підказки для нових гравців"""
        if first_time:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            # Використовуємо перекладені підказки
            tips = self.translations[self.language]["tutorial_tips"]

            for i, tip in enumerate(tips):
                text = self.font_medium.render(tip, True, (255, 255, 255))
                pos_y = self.height // 2 - len(tips) * 30 + i * 60
                pos_x = self.width // 2 - text.get_width() // 2
                surface.blit(text, (pos_x, pos_y))