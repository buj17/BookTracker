"""Реализация главного окна"""
from typing import Any, Sequence

from AddForms import AddBook, AddGenre, AddAuthor, FormMode
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import QMainWindow, QMenu, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
from UserDatabaseManager import UserDatabaseManager, GenreInUseError, AuthorInUseError
from sqlalchemy import Row
from ui import MainMenu_ui


class MainMenu(QMainWindow, MainMenu_ui.Ui_MainWindow):
    """Главное окно приложения"""

    def __init__(self, app_manager, user_id: int):
        super().__init__()
        self.setupUi(self)
        self.app_manager = app_manager
        self.user_id = user_id
        self.user_database_manager = UserDatabaseManager(user_id)
        self.user_genres: dict[str, int] = dict(self.user_database_manager.get_user_genres())
        self.user_authors: dict[str, int] = dict(self.user_database_manager.get_user_authors())
        self.clue_genre_data: Sequence[Row[tuple[Any, Any]]] | None = None
        self.clue_author_data: Sequence[Row[tuple[Any, Any]]] | None = None
        self.clue_book_data: Sequence[Row[tuple[Any, Any, Any, Any, Any]]] | None = None

        # Переключение между search-страницами
        self.showBookSearchingAction.triggered.connect(self.show_book_searching)
        self.showGenreSearchingAction.triggered.connect(self.show_genre_searching)
        self.showAuthorSearchingAction.triggered.connect(self.show_author_searching)

        # Подключаем слоты для страницы поиска книг
        self.filterNameCheckBox.toggled.connect(self.config_filter_name_edit)
        self.filterAuthorCheckBox.toggled.connect(self.config_filter_author_combo_box)
        self.filterGenreCheckBox.toggled.connect(self.config_filter_genre_combo_box)
        self.filterStatusCheckBox.toggled.connect(self.config_filter_status_combo_box)
        self.searchBooksButton.clicked.connect(self.search_books)

        # Настраиваем страницу для поиска книг
        self.config_filter_name_edit()
        self.config_filter_author_combo_box()
        self.config_filter_genre_combo_box()
        self.config_filter_status_combo_box()
        self.update_book_searching()

        # Настраиваем таблицу и список книг
        self.bookListWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookListWidget.customContextMenuRequested.connect(self.show_book_list_widget_context_menu)
        self.bookTableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookTableWidget.customContextMenuRequested.connect(self.show_book_table_widget_context_menu)
        self.bookTableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Настраиваем страницу для поиска жанров
        self.genreListWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.genreListWidget.customContextMenuRequested.connect(self.show_genre_list_widget_context_menu)
        self.searchGenresButton.clicked.connect(self.search_genres)

        # Настраиваем страницу для поиска авторов
        self.authorListWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.authorListWidget.customContextMenuRequested.connect(self.show_author_list_widget_context_menu)
        self.searchAuthorsButton.clicked.connect(self.search_authors)

        # Настраиваем триггеры для главного меню
        self.addGenreAction.triggered.connect(self.add_genre)
        self.addAuthorAction.triggered.connect(self.add_author)
        self.addBookAction.triggered.connect(self.add_book)
        self.export_csv_action.triggered.connect(self.export_csv)
        self.import_csv_action.triggered.connect(self.import_csv)

        self.load_app_images()

        self.statusBar().setStyleSheet('color: red')

    def load_app_images(self):
        """Загрузка изображения для приложения"""
        self.filter_image_label.setPixmap(QPixmap('app_images/icons8-filter-48.png'))

    def update_user_genres(self):
        """При обновлении списка жанров пользователя делаем соответствующие изменения"""
        self.user_genres: dict[str, int] = dict(self.user_database_manager.get_user_genres())
        self.search_genres()
        self.update_book_searching()

    def update_user_authors(self):
        """При обновлении списка авторов пользователя делаем соответствующие изменения"""
        self.user_authors: dict[str, int] = dict(self.user_database_manager.get_user_authors())
        self.search_authors()
        self.update_book_searching()

    def update_book_searching(self):
        """Обновляем состояние виджетов для фильтрации по жанру / автору при изменении списка жанров / авторов"""
        self.load_author_combo_box()
        self.load_genre_combo_box()

        if self.filterAuthorComboBox.count() == 0:
            self.filterAuthorCheckBox.setDisabled(True)
        else:
            self.filterAuthorCheckBox.setEnabled(True)

        if self.filterGenreComboBox.count() == 0:
            self.filterGenreCheckBox.setDisabled(True)
        else:
            self.filterGenreCheckBox.setEnabled(True)

    def show_book_searching(self):
        """Переключение на страницу поиска книг"""
        self.stackedWidget.setCurrentIndex(0)

    def show_genre_searching(self):
        """Переключение на страницу поиска жанров"""
        self.stackedWidget.setCurrentIndex(1)

    def show_author_searching(self):
        """Переключение на страницу поиска авторов"""
        self.stackedWidget.setCurrentIndex(2)

    def load_author_combo_box(self):
        """Обновляем выпадающий список авторов"""
        self.filterAuthorComboBox.clear()
        self.filterAuthorComboBox.addItems(self.user_authors.keys())

    def load_genre_combo_box(self):
        """Обновляем выпадающий список жанров"""
        self.filterGenreComboBox.clear()
        self.filterGenreComboBox.addItems(self.user_genres.keys())

    def config_filter_name_edit(self):
        """Если галочка на фильтрацию по названию включена, даем возможность пользователю задавать название"""
        self.filterNameEdit.setEnabled(self.filterNameCheckBox.isChecked())

    def config_filter_author_combo_box(self):
        """Если галочка на фильтрацию по автору включена, даем возможность пользователю задавать автора"""
        self.filterAuthorComboBox.setEnabled(self.filterAuthorCheckBox.isChecked())

    def config_filter_genre_combo_box(self):
        """Если галочка на фильтрацию по жанру включена, даем возможность пользователю задавать жанр"""
        self.filterGenreComboBox.setEnabled(self.filterGenreCheckBox.isChecked())

    def config_filter_status_combo_box(self):
        """Если галочка на фильтрацию по статусу включена, даем возможность пользователю задавать статус"""
        self.filterStatusComboBox.setEnabled(self.filterStatusCheckBox.isChecked())

    def show_genre_list_widget_context_menu(self, pos):
        """Контекстное меню для списка жанров"""
        menu = QMenu(self)
        edit_action = QAction('Редактировать жанр', self)
        delete_action = QAction('Удалить жанр', self)

        item = self.genreListWidget.itemAt(pos)
        if item is None:
            return

        edit_action_triggered: pyqtSignal | pyqtBoundSignal = edit_action.triggered
        delete_action_triggered: pyqtSignal | pyqtBoundSignal = delete_action.triggered
        edit_action_triggered.connect(self.edit_genre)
        delete_action_triggered.connect(self.delete_genre)

        menu.addActions((edit_action, delete_action))
        menu.exec(self.genreListWidget.mapToGlobal(pos))

    def search_genres(self):
        """Слот для поиска жанров"""
        title = self.genreEdit.text()
        self.clue_genre_data = self.user_database_manager.search_genres(title)
        self.update_genre_list_widget_data()

    def update_genre_list_widget_data(self):
        """Обновление результата поиска жанров"""
        self.genreListWidget.clear()
        if self.clue_genre_data:
            self.statusBar().clearMessage()
            self.genreListWidget.addItems(map(lambda record: record[1], self.clue_genre_data))
        else:
            self.statusBar().showMessage('Не найдено ни одного жанра')

    def add_genre(self):
        """Вызов окна на добавление жанра"""
        add_genre_widget = AddGenre(self, Qt.WindowType.Window, FormMode.Add, self.user_id)
        add_genre_widget.show()

    def edit_genre(self):
        """Вызов окна на редактирование жанра"""
        selected_index = self.genreListWidget.selectedIndexes()[0].row()
        genre_id: Any | int = self.clue_genre_data[selected_index][0]
        add_genre_widget = AddGenre(self, Qt.WindowType.Window, FormMode.Edit, self.user_id)
        add_genre_widget.load_genre(genre_id)
        add_genre_widget.show()

    def delete_genre(self):
        """Удаление жанра с подтверждением пользователя"""
        selected_index = self.genreListWidget.selectedIndexes()[0].row()
        genre_id, genre_title = self.clue_genre_data[selected_index]
        valid = QMessageBox.question(self,
                                     'Удаление жанра',
                                     f'Вы действительно хотите удалить жанр "{genre_title}"?',
                                     buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if valid == QMessageBox.StandardButton.Yes:
            try:
                self.user_database_manager.delete_genre(genre_id)
                self.update_user_genres()
            except GenreInUseError:
                QMessageBox.warning(self, 'Ошибка',
                                    f'Невозможно удалить жанр "{genre_title}", так как есть книги с этим жанром')

    def show_author_list_widget_context_menu(self, pos):
        """Контекстное меню для списка авторов"""
        menu = QMenu(self)
        edit_action = QAction('Редактировать автора', self)
        delete_action = QAction('Удалить автора', self)

        item = self.authorListWidget.itemAt(pos)
        if item is None:
            return

        edit_action_triggered: pyqtSignal | pyqtBoundSignal = edit_action.triggered
        delete_action_triggered: pyqtSignal | pyqtBoundSignal = delete_action.triggered
        edit_action_triggered.connect(self.edit_author)
        delete_action_triggered.connect(self.delete_author)

        menu.addActions((edit_action, delete_action))
        menu.exec(self.authorListWidget.mapToGlobal(pos))

    def search_authors(self):
        """Слот для поиска авторов"""
        title = self.authorEdit.text()
        self.clue_author_data = self.user_database_manager.search_authors(title)
        self.update_author_list_widget_data()

    def update_author_list_widget_data(self):
        """Обновление результата поиска авторов"""
        self.authorListWidget.clear()
        if self.clue_author_data:
            self.statusBar().clearMessage()
            self.authorListWidget.addItems(map(lambda record: record[1], self.clue_author_data))
        else:
            self.statusBar().showMessage('Не найдено ни одного автора')

    def add_author(self):
        """Вызов окна на добавление автора"""
        add_author_widget = AddAuthor(self, Qt.WindowType.Window, FormMode.Add, self.user_id)
        add_author_widget.show()

    def edit_author(self):
        """Вызов окна на редактирование жанра"""
        selected_index = self.authorListWidget.selectedIndexes()[0].row()
        author_id: Any | int = self.clue_author_data[selected_index][0]
        add_author_widget = AddAuthor(self, Qt.WindowType.Window, FormMode.Edit, self.user_id)
        add_author_widget.load_author(author_id)
        add_author_widget.show()

    def delete_author(self):
        """Удаление автора с подтверждением пользователя"""
        selected_index = self.authorListWidget.selectedIndexes()[0].row()
        author_id, author_title = self.clue_author_data[selected_index]
        valid = QMessageBox.question(self,
                                     'Удаление автора',
                                     f'Вы действительно хотите удалить автора "{author_title}"?',
                                     buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if valid == QMessageBox.StandardButton.Yes:
            try:
                self.user_database_manager.delete_author(author_id)
                self.update_user_authors()
            except AuthorInUseError:
                QMessageBox.warning(self, 'Ошибка',
                                    f'Невозможно удалить автора "{author_title}", так как есть книги с этим автором')

    def search_books(self):
        """Слот для поиска книг"""
        title = self.filterNameEdit.text().lower() if self.filterNameCheckBox.isChecked() else None
        author = self.filterAuthorComboBox.currentText().lower() if self.filterAuthorCheckBox.isChecked() else None
        genre = self.filterGenreComboBox.currentText().lower() if self.filterGenreCheckBox.isChecked() else None
        status = self.filterStatusComboBox.currentText() if self.filterStatusCheckBox.isChecked() else None
        sort = self.sortComboBox.currentText()

        self.clue_book_data = self.user_database_manager.search_books(title, author, genre, status, sort)

        if self.displayTypeComboBox.currentText() == 'Список':
            self.list_table_stack.setCurrentIndex(0)
            self.update_book_list_widget_data()
        elif self.displayTypeComboBox.currentText() == 'Таблица':
            self.list_table_stack.setCurrentIndex(1)
            self.update_book_table_widget_data()

        if not self.clue_book_data:
            self.statusBar().showMessage('Не найдено ни одной книги')
        else:
            self.statusBar().clearMessage()

    def update_book_list_widget_data(self):
        """Обновление списка с книгами"""
        self.bookListWidget.clear()
        self.bookListWidget.addItems(map(lambda record: record[1], self.clue_book_data))

    def update_book_table_widget_data(self):
        """Обновление таблицы с книгами"""
        header = ('Название', 'Автор', 'Жанр', 'Статус')
        self.bookTableWidget.clear()
        self.bookTableWidget.setColumnCount(len(header))
        self.bookTableWidget.setHorizontalHeaderLabels(header)
        self.bookTableWidget.setRowCount(0)

        table_elements = map(lambda record: (record[1], record[2], record[3], record[4]), self.clue_book_data)

        for i, line in enumerate(table_elements):
            self.bookTableWidget.setRowCount(self.bookTableWidget.rowCount() + 1)
            for j, element in enumerate(line):
                self.bookTableWidget.setItem(i, j, QTableWidgetItem(element))

        self.bookTableWidget.resizeColumnsToContents()

    def show_book_list_widget_context_menu(self, pos):
        """Контекстное меню для списка книг"""
        menu = QMenu(self)
        edit_action = QAction('Редактировать книгу', self)
        delete_action = QAction('Удалить книгу', self)

        item = self.bookListWidget.itemAt(pos)
        if item is None:
            return

        edit_action_triggered: pyqtSignal | pyqtBoundSignal = edit_action.triggered
        delete_action_triggered: pyqtSignal | pyqtBoundSignal = delete_action.triggered
        edit_action_triggered.connect(self._edit_book_from_list)
        delete_action_triggered.connect(self._delete_book_from_list)

        menu.addActions((edit_action, delete_action))
        menu.exec(self.bookListWidget.mapToGlobal(pos))

    def show_book_table_widget_context_menu(self, pos):
        """Контекстное меню для таблицы книг"""
        menu = QMenu(self)
        edit_action = QAction('Редактировать книгу', self)
        delete_action = QAction('Удалить книгу', self)

        item = self.bookTableWidget.itemAt(pos)
        if item is None:
            return

        edit_action_triggered: pyqtSignal | pyqtBoundSignal = edit_action.triggered
        delete_action_triggered: pyqtSignal | pyqtBoundSignal = delete_action.triggered
        edit_action_triggered.connect(self._edit_book_from_table)
        delete_action_triggered.connect(self._delete_book_from_table)

        menu.addActions((edit_action, delete_action))
        menu.exec(self.bookListWidget.mapToGlobal(pos))

    def add_book(self):
        """Вызов окна на добавление книги"""
        if not self.user_authors:
            message = 'В вашей личной библиотеке нет ни одного автора. Добавьте автора, чтобы добавить книгу'
            QMessageBox.warning(self, 'Ошибка',
                                message)
            return

        if not self.user_genres:
            message = 'В вашей личной библиотеке нет ни одного жанра. Добавьте жанр, чтобы добавить книгу'
            QMessageBox.warning(self, 'Ошибка',
                                message)
            return

        add_book_widget = AddBook(self, Qt.WindowType.Window, FormMode.Add,
                                  self.user_id, self.user_genres, self.user_authors)
        add_book_widget.show()

    def edit_book(self, book_id):
        """Вызов окна на редактирование книги"""
        add_book_widget = AddBook(self, Qt.WindowType.Window, FormMode.Edit,
                                  self.user_id, self.user_genres, self.user_authors)
        add_book_widget.load_book(book_id)
        add_book_widget.show()

    def delete_book(self, book_id):
        """Удаление книги с подтверждением пользователя"""
        book_title = self.user_database_manager.get_book(book_id)[0]
        valid = QMessageBox.question(self,
                                     'Удаление книги',
                                     f'Вы действительно хотите удалить книгу "{book_title}"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if valid == QMessageBox.StandardButton.Yes:
            self.user_database_manager.delete_book(book_id)
            self.search_books()

    def _edit_book_from_list(self):
        selected_index = self.bookListWidget.selectedIndexes()[0].row()
        book_id: Any | int = self.clue_book_data[selected_index][0]
        self.edit_book(book_id)

    def _delete_book_from_list(self):
        selected_index = self.bookListWidget.selectedIndexes()[0].row()
        book_id: Any | int = self.clue_book_data[selected_index][0]
        self.delete_book(book_id)

    def _edit_book_from_table(self):
        selected_index = self.bookTableWidget.selectedIndexes()[0].row()
        book_id: Any | int = self.clue_book_data[selected_index][0]
        self.edit_book(book_id)

    def _delete_book_from_table(self):
        selected_index = self.bookTableWidget.selectedIndexes()[0].row()
        book_id: Any | int = self.clue_book_data[selected_index][0]
        self.delete_book(book_id)

    def export_csv(self):
        """Вызов файлового диалога для экспорта книг в формате csv"""
        filename = QFileDialog.getSaveFileName(self, 'Экспорт csv', '',
                                               'CSV files (*.csv);;All files (*)')[0]
        if filename:
            self.user_database_manager.export_csv(filename)

    def import_csv(self):
        """Вызов файлового диалога для импорта книг в формате csv.
        Все предыдущие книги пользователя будут удалены и полностью заменены на экспортированные"""
        filename = QFileDialog.getOpenFileName(self, 'Импорт csv', '',
                                               'CSV files (*.csv);;All files (*)')[0]
        if filename:
            message = 'Вы уверены, что хотите импортировать csv? Все ваши книги будут удалены и заменены на новые'

            valid = QMessageBox.question(self,
                                         'Импорт csv',
                                         message,
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if valid == QMessageBox.StandardButton.Yes:
                self.user_database_manager.import_csv(filename)

        self.update_user_authors()
        self.update_user_genres()
        self.search_books()

    def closeEvent(self, a0):
        """При закрытии окна закрываем подключение к базе данных"""
        self.user_database_manager.close()
