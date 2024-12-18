import pygame
import math
import random

class Particle:
    def __init__(self, x, y, color, size, speed):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.lifetime = 255
        self.vx = math.cos(self.angle) * speed
        self.vy = math.sin(self.angle) * speed

    def update(self):
        """
        Оновлення стану частинки: рух та зменшення часу життя

        :return: True, якщо частинка ще активна, інакше False
        """
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 2
        return self.lifetime > 0

    def draw(self, screen):
        """
        Малювання частинки з урахуванням поточного стану

        :param screen: поверхня для малювання
        """
        alpha = max(0, min(255, self.lifetime))
        color_with_alpha = (*self.color, alpha)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))