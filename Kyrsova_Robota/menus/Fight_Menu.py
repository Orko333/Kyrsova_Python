from menus.Menu_For_Bot import Menu_For_Bot
from menus.One_On_One_Menu import One_ON_One
from menus.Menu_Class import Menu

class Fight_menu(Menu):
    def __init__(self):
        """
        Ініціалізує меню бою.
        """
        super().__init__("CHOMP!")
        self.buttons = [
            ("1 на 1", self.one_on_one),
            ("Гра з Ботом", self.fight_with_bot),
            ("Назад", self.back)
        ]
        self.setup_buttons()

    def one_on_one(self):
        """
        Запускає гру 1 на 1.
        """
        start_game = One_ON_One()
        start_game.run()

    def fight_with_bot(self):
        """
        Запускає гру з ботом.
        """
        start_game = Menu_For_Bot()
        start_game.run()

    def back(self):
        """
        Повертає до попереднього меню.
        """
        self.running = False