import pygame


class TextureManager:
    """
    Клас для централізованого управління текстурами
    Забезпечує завантаження текстури лише один раз
    """
    _textures = {}

    @classmethod
    def get_texture(cls, filename, size):
        """
        Отримання текстури. Якщо текстура ще не завантажена - завантажує.

        :param filename: назва файлу текстури
        :param size: бажаний розмір текстури
        :return: масштабована текстура
        """
        # Унікальний ключ кешу з назви файлу та розміру
        cache_key = (filename, size)

        # Якщо текстура ще не завантажена
        if cache_key not in cls._textures:
            try:
                # Завантаження оригінальної текстури
                original_texture = pygame.image.load(filename).convert_alpha()
                # Масштабування текстури


                scaled_texture = pygame.transform.scale(original_texture, (size,size))
                # Збереження в кеш
                cls._textures[cache_key] = scaled_texture

            except pygame.error:
                print(f"Помилка завантаження текстури '{filename}'")
                return None

        return cls._textures[cache_key]
