"""Главный файл для запуска приложения"""
import sys

import qdarktheme
from LoginWindow import LoginWindow
from MainMenu import MainMenu
from PyQt6.QtWidgets import QApplication


class AppManager:
    """Данный класс нужен для переключения между окном регистрации и главным окном"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_user_id: int | None = None
        self.login_window: LoginWindow | None = None
        self.main_menu: MainMenu | None = None

    def run(self):
        """Запуск программы: первым делом показывается окно входа"""
        self.login_window = LoginWindow(self)
        self.login_window.show()
        self.app.exec()

    def show_main_menu(self, user_id: int):
        """После входа в аккаунт показывается главное меню"""
        self.login_window.close()
        self.main_menu = MainMenu(self, user_id)
        self.main_menu.show()


def except_hook(cls, exception, traceback):
    """Функция для переопределения sys.excepthook"""
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app_manager = AppManager()
    qdarktheme.setup_theme()
    sys.excepthook = except_hook
    app_manager.run()
