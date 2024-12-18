import math
import random
from Blocks_and_textures.Texture_Manager import *

class AnimatedBlock:
    def __init__(self, x, y, poison, block_size, block_height):
        """
        Ініціалізація анімованого блоку

        :param x: позиція X блоку
        :param y: позиція Y блоку
        :param poison: чи є блок отруйним
        :param block_size: розмір блоку
        :param block_height: висота блоку
        """
        self.x = x
        self.y = y
        self.target_y = y
        self.is_poison = poison

        self.colors = {
            "red": (255, 0, 0),
            "dark_chocolate": (50, 25, 10),
            "milk_chocolate": (120, 70, 35),
            "light_chocolate": (170, 100, 50),
            "border": (35, 18, 8),
            "highlight": (200, 150, 100)
        }

        self.block_size = block_size
        self.block_height = block_height

        self.falling = False
        self.fall_speed = 0
        self.gravity = 0.3
        self.rotation = 0
        self.scale = 1.0

        self.shine_offset = 0
        self.glow_intensity = 0
        self.creation_time = pygame.time.get_ticks()
        self.particles = []

        self.texture = TextureManager.get_texture("Blocks_and_textures/cherep.png", block_size) if poison else None
        self.last_scale = 1.0
        self.cached_texture = None

    def update(self):
        """
        Оновлення стану блоку: анімація падіння, частинки, світіння

        :return: True, якщо блок ще активний, інакше False
        """
        current_time = pygame.time.get_ticks()
        time_alive = (current_time - self.creation_time) / 1000.0

        if self.falling:
            self.fall_speed += self.gravity
            self.y += self.fall_speed
            self.rotation = (self.rotation + 4) % 360
            self.scale = max(0, self.scale - 0.015)

            if random.random() < 0.2:
                self.particles.append([
                    self.x + random.uniform(0, self.block_size),
                    self.y + random.uniform(0, self.block_size),
                    random.uniform(-1.5, 1.5),
                    random.uniform(-1.5, 1.5),
                    random.uniform(2.5, 5),
                    (*self.colors["dark_chocolate"], 255)
                ])

            return self.y < self.target_y + 700 and self.scale > 0
        else:
            self.shine_offset = math.sin(time_alive * 2) * 0.25
            self.glow_intensity = (math.sin(time_alive * 3) + 1) * 0.6
            return True

    def draw(self, screen):
        """
        Малювання блоку з урахуванням поточного стану

        :param screen: поверхня для малювання
        """
        current_size = int(self.block_size * self.scale)
        if current_size <= 0:
            return

        block_surface = pygame.Surface((current_size, current_size), pygame.SRCALPHA)

        for i in range(current_size):
            progress = i / current_size
            shine = max(0, 1 - abs(progress - 0.5 - self.shine_offset) * 3)
            base_color = [
                self.colors["dark_chocolate"][j] * (1 - shine) +
                self.colors["milk_chocolate"][j] * shine +
                self.colors["light_chocolate"][j] * (shine ** 2) * 0.3
                for j in range(3)
            ]
            pygame.draw.line(block_surface, (*base_color, 255), (0, i), (current_size, i))

        border_width = 6
        pygame.draw.rect(block_surface, self.colors["border"], (0, 0, current_size, current_size), border_width)
        pygame.draw.rect(block_surface, self.colors["highlight"] + (100,),
                         (border_width, border_width, current_size - 2 * border_width, current_size - 2 * border_width), 2)

        inner_margin = 12
        inner_rect = pygame.Rect(inner_margin, inner_margin,
                                 current_size - 2 * inner_margin,
                                 current_size - 2 * inner_margin)
        inner_color = (*self.colors["milk_chocolate"], 180)
        pygame.draw.rect(block_surface, inner_color, inner_rect)

        if not self.falling:
            gloss_surface = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
            for x in range(0, current_size, 3):
                gloss_alpha = int(30 * math.sin(x / current_size * math.pi))
                pygame.draw.line(gloss_surface, (255, 255, 255, gloss_alpha), (x, 0), (x + current_size // 2, current_size), 2)
            block_surface.blit(gloss_surface, (0, 0))

            shadow_surface = pygame.Surface((current_size + 14, current_size + 14), pygame.SRCALPHA)
            shadow_rect = pygame.Rect(7, 7, current_size, current_size)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_rect)
            screen.blit(shadow_surface, (self.x - 7, self.y - 7))

            if self.is_poison and self.texture:
                if self.falling and abs(self.scale - self.last_scale) > 0.01:
                    current_size = int(self.block_size * self.scale)
                    self.cached_texture = pygame.transform.scale(self.texture, (current_size, current_size))
                    self.last_scale = self.scale

                texture_to_draw = self.cached_texture if self.cached_texture else self.texture
                screen.blit(texture_to_draw, (self.x, self.y))

        if self.falling:
            for i in range(4):
                blur_surface = pygame.transform.rotate(block_surface, self.rotation + i * 2)
                blur_rect = blur_surface.get_rect(center=(self.x + current_size // 2, self.y + current_size // 2))
                blur_surface.set_alpha(35)
                screen.blit(blur_surface, blur_rect.topleft)

            rotated_surface = pygame.transform.rotate(block_surface, self.rotation)
            new_rect = rotated_surface.get_rect(center=(self.x + current_size // 2, self.y + current_size // 2))
            screen.blit(rotated_surface, new_rect.topleft)
        else:
            screen.blit(block_surface, (self.x, self.y))

        for particle in self.particles[:]:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[4] -= 0.12
            if particle[4] > 0:
                pygame.draw.circle(screen, particle[5][:4], (int(particle[0]), int(particle[1])), int(particle[4]))
                pygame.draw.circle(screen, (*self.colors["highlight"], 100),
                                   (int(particle[0] - 1), int(particle[1] - 1)), int(particle[4] / 2))
            else:
                self.particles.remove(particle)