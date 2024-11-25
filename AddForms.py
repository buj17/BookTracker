"""Реализация окон для добавления / редактирования"""
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox
from UserDatabaseManager import UserDatabaseManager
from sqlalchemy.exc import IntegrityError
from ui import AddGenre_ui, AddAuthor_ui, AddBook_ui


class FormMode:
    """Константы, задающие режим открытия окна: Add - добавление, Edit - редактирование"""
    Add = 0
    Edit = 1


class AddGenre(QWidget, AddGenre_ui.Ui_Form):
    """Окно для добавления / редактирования жанров"""
    def __init__(self, parent: QMainWindow | Any, flags: Qt.WindowType, mode: int, user_id: int):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.mode = mode
        self.genre_id = None
        self.user_database_manager = UserDatabaseManager(user_id)
        self.parent_widget: QMainWindow | Any = parent

        if self.mode == FormMode.Add:
            self.pushButton.setText('Добавить')
        elif self.mode == FormMode.Edit:
            self.pushButton.setText('Редактировать')

        self.pushButton.clicked.connect(self.execute)

        self.errorLabel.setStyleSheet('color: red')

    def execute(self):
        """Выполнение запроса при нажатии кнопки"""
        title = self.lineEdit.text()

        if not title:
            self.errorLabel.setText('Введите название жанра')
            return

        try:
            if self.mode == FormMode.Add:
                self.user_database_manager.add_genre(title)
            elif self.mode == FormMode.Edit:
                self.user_database_manager.edit_genre(self.genre_id, title)
            self.parent_widget.update_user_genres()
            self.close()
        except IntegrityError:
            self.user_database_manager.rollback()
            self.errorLabel.setText('Данный жанр уже есть')

    def load_genre(self, genre_id: int):
        """Загрузка информации о жанре в режиме редактирования"""
        self.genre_id = genre_id
        title = self.user_database_manager.get_genre(genre_id)
        self.lineEdit.setText(title)

    def closeEvent(self, a0):
        """Закрытие подключения к базе данных при закрытии окна"""
        self.user_database_manager.close()


class AddAuthor(QWidget, AddAuthor_ui.Ui_Form):
    """Окно для добавления / редактирования авторов"""
    def __init__(self, parent: QMainWindow | Any, flags: Qt.WindowType, mode: int, user_id: int):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.mode = mode
        self.author_id = None
        self.user_database_manager = UserDatabaseManager(user_id)
        self.parent_widget: QMainWindow | Any = parent

        if self.mode == FormMode.Add:
            self.pushButton.setText('Добавить')
        elif self.mode == FormMode.Edit:
            self.pushButton.setText('Редактировать')

        self.pushButton.clicked.connect(self.execute)

        self.errorLabel.setStyleSheet('color: red')

    def execute(self):
        """Выполнение запроса при нажатии кнопки"""
        title = self.lineEdit.text()

        if not title:
            self.errorLabel.setText('Введите название автора')

        try:
            if self.mode == FormMode.Add:
                self.user_database_manager.add_author(title)
            elif self.mode == FormMode.Edit:
                self.user_database_manager.edit_author(self.author_id, title)
            self.parent_widget.update_user_authors()
            self.close()
        except IntegrityError:
            self.user_database_manager.rollback()
            self.errorLabel.setText('Данный автор уже есть')

    def load_author(self, author_id):
        """Загрузка информации об авторе в режиме редактирования"""
        self.author_id = author_id
        title = self.user_database_manager.get_author(author_id)
        self.lineEdit.setText(title)

    def closeEvent(self, a0):
        """Закрытие подключения к базе данных при закрытии окна"""
        self.user_database_manager.close()


class AddBook(QWidget, AddBook_ui.Ui_Form):
    """Окно для добавления / редактирования книг"""
    def __init__(self, parent: QMainWindow | Any,
                 flags: Qt.WindowType,
                 mode: int,
                 user_id: int,
                 user_genres: dict[str, int],
                 user_authors: dict[str, int]):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.mode = mode
        self.user_genres = user_genres
        self.user_authors = user_authors
        self.book_id = None
        self.user_database_manager = UserDatabaseManager(user_id)
        self.parent_widget: QMainWindow | Any = parent

        self.load_genres()
        self.load_authors()

        if self.mode == FormMode.Add:
            self.pushButton.setText('Добавить')
        elif self.mode == FormMode.Edit:
            self.pushButton.setText('Редактировать')

        self.pushButton.clicked.connect(self.execute)

    def execute(self):
        """Выполнение запроса при нажатии кнопки"""
        title = self.titleLineEdit.text()
        author_id_book_fk = self.user_authors[self.authorComboBox.currentText()]
        genre_id_book_fk = self.user_genres[self.genreComboBox.currentText()]
        status = self.statusComboBox.currentText()

        if not title:
            QMessageBox.warning(self, 'Ошибка', 'Введите название книги')
            return

        if self.mode == FormMode.Add:
            self.user_database_manager.add_book(title, author_id_book_fk, genre_id_book_fk, status)
            self.parent_widget.search_books()
            self.close()
        elif self.mode == FormMode.Edit:
            self.user_database_manager.edit_book(self.book_id, title, author_id_book_fk, genre_id_book_fk, status)
            self.parent_widget.search_books()
            self.close()

    def load_genres(self):
        """Загрузка жанров пользователя"""
        self.genreComboBox.clear()
        self.genreComboBox.addItems(self.user_genres.keys())

    def load_authors(self):
        """Загрузка авторов пользователя"""
        self.authorComboBox.clear()
        self.authorComboBox.addItems(self.user_authors.keys())

    def load_book(self, book_id: int):
        """Загрузка информации о книге в режиме редактирования"""
        self.book_id = book_id
        title, author, genre, status = self.user_database_manager.get_book(book_id)

        self.titleLineEdit.setText(title)
        self.authorComboBox.setCurrentText(author)
        self.genreComboBox.setCurrentText(genre)
        self.statusComboBox.setCurrentText(status)

    def closeEvent(self, a0):
        """Закрытие подключения к базе данных при закрытии окна"""
        self.user_database_manager.close()
