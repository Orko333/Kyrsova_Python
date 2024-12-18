import pygame
import os

from Files import Configs


class SoundManager:
    def __init__(self, sounds_directory='sounds', num_channels=8):
        """
        Ініціалізує менеджер звуків з підтримкою множинних каналів.

        :param sounds_directory: Директорія з файлами звуків (за замовчуванням 'sounds')
        :param num_channels: Кількість звукових каналів для одночасного відтворення (за замовчуванням 8)
        """
        pygame.mixer.init()

        # Встановлення кількості каналів
        pygame.mixer.set_num_channels(num_channels)
        self.num_channels = num_channels

        # Словник для зберігання звуків
        self.sounds = {}

        # Список каналів для трекінгу
        self.channels = [pygame.mixer.Channel(i) for i in range(num_channels)]

        # Музичні налаштування
        self.music = None
        self.sounds_directory = sounds_directory

        # Автоматичне завантаження звуків
        self.load_sounds_from_directory()

    def load_sounds_from_directory(self):
        """
        Автоматично завантажує всі звукові файли з вказаної директорії.
        Підтримує формати: .wav, .mp3, .ogg
        """
        if not os.path.exists(self.sounds_directory):
            print(f"Директорія звуків {self.sounds_directory} не існує.")
            return

        for filename in os.listdir(self.sounds_directory):
            if filename.endswith(('.wav', '.mp3', '.ogg')):
                sound_name = os.path.splitext(filename)[0]
                sound_path = os.path.join(self.sounds_directory, filename)
                self.load_sound(sound_name, sound_path)

    def load_sound(self, name, file_path):
        """
        Завантаження окремого звуку.

        :param name: Назва звуку (унікальний ідентифікатор)
        :param file_path: Шлях до файлу звуку
        """
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            print(f"Звук '{name}' успішно завантажено.")
        except pygame.error as e:
            print(f"Помилка при завантаженні звуку '{name}': {e}")

    def play_sound(self, name, loops=0, volume=Configs.volume, priority=False):
        """
        Відтворення звуку з підтримкою множинних каналів.

        :param name: Назва звуку для відтворення
        :param loops: Кількість повторень (-1 для нескінченного повторення)
        :param volume: Гучність звуку (0.0 - 1.0)
        :param priority: Якщо True, намагається перервати інший звук
        """
        if name not in self.sounds:
            print(f"Звук '{name}' не знайдено.")
            return

        sound = self.sounds[name]

        # Знаходження вільного каналу або пріоритетного відтворення
        if priority:
            # Намагаємося перервати найменш пріоритетний канал
            for channel in self.channels:
                if not channel.get_busy():
                    channel.play(sound, loops)
                    channel.set_volume(volume)
                    return

            # Якщо всі канали зайняті, перериваємо останній канал
            self.channels[-1].stop()
            self.channels[-1].play(sound, loops)
            self.channels[-1].set_volume(volume)
        else:
            # Стандартне відтворення на першому вільному каналі
            for channel in self.channels:
                if not channel.get_busy():
                    channel.play(sound, loops)
                    channel.set_volume(volume)
                    return

            # Якщо всі канали зайняті, друкуємо повідомлення
            print(f"Всі канали зайняті. Неможливо відтворити звук '{name}'")

    def stop_sound(self, name):
        """
        Зупинка конкретного звуку на всіх каналах.

        :param name: Назва звуку для зупинки
        """
        if name not in self.sounds:
            print(f"Звук '{name}' не знайдено.")
            return

        sound = self.sounds[name]
        for channel in self.channels:
            if channel.get_sound() == sound:
                channel.stop()

    def stop_all_sounds(self):
        """
        Зупинка всіх звуків на всіх каналах.
        """
        pygame.mixer.stop()

    def get_channel_count(self):
        """
        Повертає кількість каналів.

        :return: Кількість каналів
        """
        return self.num_channels

    def is_channel_busy(self):
        """
        Перевіряє, чи зайняті всі канали.

        :return: True, якщо всі канали зайняті, інакше False
        """
        return all(channel.get_busy() for channel in self.channels)

