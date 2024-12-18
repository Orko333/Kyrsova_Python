import ctypes
import os

class ChompBot:
    def __init__(self, dificulty):
        """
        Ініціалізація бота з використанням C-бібліотеки.

        :param dll_path: шлях до DLL бібліотеки
        """
        # Додати каталог, де знаходяться бібліотеки
        try:
            os.add_dll_directory(r"C:\msys64\mingw64\bin")
        except:
            print("Помилка модуль C++ не було знайдено")
        
        # Завантажити DLL
        if dificulty == 'easy':
            dll_path = r'botu\libchomp_ai_easy.dll'
        elif dificulty == 'medium':
            dll_path = r'botu\libchomp_ai_medium.dll'
        elif dificulty == 'hard':
            dll_path = r'botu\libchomp_ai_hard.dll'
        self.lib = ctypes.CDLL(dll_path)

        # Визначення структури Move
        class Move(ctypes.Structure):
            _fields_ = [("row", ctypes.c_int32),
                        ("col", ctypes.c_int32)]

        self.Move = Move

        # Налаштування типів вхідних і вихідних даних
        self.lib.choose_chomp_move.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.lib.choose_chomp_move.restype = Move

    def get_move(self, board, poison_pos):
        """
        Отримання ходу від бота для поточного стану дошки.

        :param board: поточний стан дошки (2D список булевих значень)
        :param poison_pos: позиція отруєного блоку
        :return: кортеж (row, col) або None, якщо хід неможливий
        """
        # Перетворення дошки в одновимірний масив цілих чисел
        rows = len(board)
        cols = len(board[0])
        flat_board = [1 if cell else 0 for row in board for cell in row]
        c_board = (ctypes.c_int32 * (rows * cols))(*flat_board)



        # Виклик функції з бібліотеки
        move = self.lib.choose_chomp_move(c_board, rows, cols, poison_pos[0], poison_pos[1])

        # Перевірка, чи є коректний хід
        if 0 <= move.row < rows and 0 <= move.col < cols and board[move.row][move.col]:
            return move.row, move.col
        return None
