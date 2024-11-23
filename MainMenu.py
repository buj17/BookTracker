import os.path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import QMainWindow, QMenu, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
from UserDatabaseManager import UserDatabaseManager, GenreInUseError, AuthorInUseError
from AddForms import AddBook, AddGenre, AddAuthor, FormMode
from ui import MainMenu_ui


class MainMenu(QMainWindow, MainMenu_ui.Ui_MainWindow):
    def __init__(self, app_manager, user_id):
        super().__init__()
        self.setupUi(self)
        self.app_manager = app_manager
        self.user_id = user_id
        self.user_database_manager = UserDatabaseManager(user_id)
        self.user_genres: dict[str, int] = dict(self.user_database_manager.get_user_genres())
        self.user_authors: dict[str, int] = dict(self.user_database_manager.get_user_authors())

        self.filter_image_label.setPixmap(QPixmap('ui/icons8-filter-48.png'))

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
        self.load_author_combo_box()
        self.load_genre_combo_box()

        if self.filterAuthorComboBox.count() == 0:
            self.filterAuthorCheckBox.setDisabled(True)
        if self.filterGenreComboBox.count() == 0:
            self.filterGenreCheckBox.setDisabled(True)

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

        self.addGenreAction.triggered.connect(self.add_genre)
        self.addAuthorAction.triggered.connect(self.add_author)
        self.addBookAction.triggered.connect(self.add_book)
        self.export_csv_action.triggered.connect(self.export_csv)
        self.import_csv_action.triggered.connect(self.import_csv)

        self.statusBar().setStyleSheet('color: red')

    def update_user_genres(self):
        self.user_genres: dict[str, int] = dict(self.user_database_manager.get_user_genres())
        self.search_genres()
        self.load_genre_combo_box()

    def update_user_authors(self):
        self.user_authors: dict[str, int] = dict(self.user_database_manager.get_user_authors())
        self.search_authors()
        self.load_author_combo_box()

    def show_book_searching(self):
        self.stackedWidget.setCurrentIndex(0)

    def show_genre_searching(self):
        self.stackedWidget.setCurrentIndex(1)

    def show_author_searching(self):
        self.stackedWidget.setCurrentIndex(2)

    def load_author_combo_box(self):
        self.filterAuthorComboBox.clear()
        self.filterAuthorComboBox.addItems(self.user_authors.keys())

    def load_genre_combo_box(self):
        self.filterGenreComboBox.clear()
        self.filterGenreComboBox.addItems(self.user_genres.keys())

    def config_filter_name_edit(self):
        self.filterNameEdit.setEnabled(self.filterNameCheckBox.isChecked())

    def config_filter_author_combo_box(self):
        self.filterAuthorComboBox.setEnabled(self.filterAuthorCheckBox.isChecked())

    def config_filter_genre_combo_box(self):
        self.filterGenreComboBox.setEnabled(self.filterGenreCheckBox.isChecked())

    def config_filter_status_combo_box(self):
        self.filterStatusComboBox.setEnabled(self.filterStatusCheckBox.isChecked())

    def show_genre_list_widget_context_menu(self, pos):
        menu = QMenu(self)
        editAction = QAction('Редактировать жанр', self)
        deleteAction = QAction('Удалить жанр', self)

        item = self.genreListWidget.itemAt(pos)
        if item is None:
            return

        editAction.triggered.connect(self.edit_genre)
        deleteAction.triggered.connect(self.delete_genre)

        menu.addActions((editAction, deleteAction))
        menu.exec(self.genreListWidget.mapToGlobal(pos))

    def search_genres(self):
        title = self.genreEdit.text()
        self.clue_genre_data = self.user_database_manager.search_genres(title)
        self.update_genre_list_widget_data()

    def update_genre_list_widget_data(self):
        self.genreListWidget.clear()
        if self.clue_genre_data:
            self.statusBar().clearMessage()
            self.genreListWidget.addItems(map(lambda record: record[1], self.clue_genre_data))
        else:
            self.statusBar().showMessage('Не найдено ни одного жанра')

    def add_genre(self):
        add_genre_widget = AddGenre(self, Qt.WindowType.Window, FormMode.Add, self.user_id)
        add_genre_widget.show()

    def edit_genre(self):
        selected_index = self.genreListWidget.selectedIndexes()[0].row()
        genre_id: Any | int = self.clue_genre_data[selected_index][0]
        add_genre_widget = AddGenre(self, Qt.WindowType.Window, FormMode.Edit, self.user_id)
        add_genre_widget.load_genre(genre_id)
        add_genre_widget.show()

    def delete_genre(self):
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
        menu = QMenu(self)
        editAction = QAction('Редактировать автора', self)
        deleteAction = QAction('Удалить автора', self)

        item = self.authorListWidget.itemAt(pos)
        if item is None:
            return

        editAction.triggered.connect(self.edit_author)
        deleteAction.triggered.connect(self.delete_author)

        menu.addActions((editAction, deleteAction))
        menu.exec(self.authorListWidget.mapToGlobal(pos))

    def search_authors(self):
        title = self.authorEdit.text()
        self.clue_author_data = self.user_database_manager.search_authors(title)
        self.update_author_list_widget_data()

    def update_author_list_widget_data(self):
        self.authorListWidget.clear()
        if self.clue_author_data:
            self.statusBar().clearMessage()
            self.authorListWidget.addItems(map(lambda record: record[1], self.clue_author_data))
        else:
            self.statusBar().showMessage('Не найдено ни одного автора')

    def add_author(self):
        add_author_widget = AddAuthor(self, Qt.WindowType.Window, FormMode.Add, self.user_id)
        add_author_widget.show()

    def edit_author(self):
        selected_index = self.authorListWidget.selectedIndexes()[0].row()
        author_id: Any | int = self.clue_author_data[selected_index][0]
        add_author_widget = AddAuthor(self, Qt.WindowType.Window, FormMode.Edit, self.user_id)
        add_author_widget.load_author(author_id)
        add_author_widget.show()

    def delete_author(self):
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
        self.bookListWidget.clear()
        self.bookListWidget.addItems(map(lambda record: record[1], self.clue_book_data))

    def update_book_table_widget_data(self):
        header = ('Название', 'Автор', 'Жанр', 'Статус')
        self.bookTableWidget.clear()
        self.bookTableWidget.setColumnCount(len(header))
        self.bookTableWidget.setHorizontalHeaderLabels(header)
        self.bookTableWidget.setRowCount(0)

        table_elements = map(lambda record: (record[1], record[2], record[3], record[4]), self.clue_book_data)

        for i, record in enumerate(table_elements):
            self.bookTableWidget.setRowCount(self.bookTableWidget.rowCount() + 1)
            for j, element in enumerate(record):
                self.bookTableWidget.setItem(i, j, QTableWidgetItem(element))

        self.bookTableWidget.resizeColumnsToContents()

    def show_book_list_widget_context_menu(self, pos):
        menu = QMenu(self)
        editAction = QAction('Редактировать книгу', self)
        deleteAction = QAction('Удалить книгу', self)

        item = self.bookListWidget.itemAt(pos)
        if item is None:
            return

        editAction.triggered.connect(self._edit_book_from_list)
        deleteAction.triggered.connect(self._delete_book_from_list)

        menu.addActions((editAction, deleteAction))
        menu.exec(self.bookListWidget.mapToGlobal(pos))

    def show_book_table_widget_context_menu(self, pos):
        menu = QMenu(self)
        editAction = QAction('Редактировать книгу', self)
        deleteAction = QAction('Удалить книгу', self)

        item = self.bookTableWidget.itemAt(pos)
        if item is None:
            return

        editAction.triggered.connect(self._edit_book_from_table)
        deleteAction.triggered.connect(self._delete_book_from_table)

        menu.addActions((editAction, deleteAction))
        menu.exec(self.bookListWidget.mapToGlobal(pos))

    def add_book(self):
        add_book_widget = AddBook(self, Qt.WindowType.Window, FormMode.Add,
                                  self.user_id, self.user_genres, self.user_authors)
        add_book_widget.show()

    def edit_book(self, book_id):
        add_book_widget = AddBook(self, Qt.WindowType.Window, FormMode.Edit,
                                  self.user_id, self.user_genres, self.user_authors)
        add_book_widget.load_book(book_id)
        add_book_widget.show()

    def delete_book(self, book_id):
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
        filename = QFileDialog.getSaveFileName(self, 'Экспорт csv', '',
                                               'CSV files (*.csv);;All files (*)')[0]
        if filename:
            self.user_database_manager.export_csv(filename)

    def import_csv(self):
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
        self.user_database_manager.close()
