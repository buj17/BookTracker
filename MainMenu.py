from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QMenu
from UserDatabaseManager import UserDatabaseManager
from ui import MainMenu_ui


class MainMenu(QMainWindow, MainMenu_ui.Ui_MainWindow):
    def __init__(self, app_manager, user_id):
        super().__init__()
        self.setupUi(self)
        self.app_manager = app_manager
        self.user_database_manager = UserDatabaseManager(user_id)

        self.showBookSearchingAction.triggered.connect(self.show_book_searching)
        self.filterNameCheckBox.toggled.connect(self.config_filter_name_edit)
        self.filterAuthorCheckBox.toggled.connect(self.config_filter_author_combo_box)
        self.filterGenreCheckBox.toggled.connect(self.config_filter_genre_combo_box)
        self.filterStatusCheckBox.toggled.connect(self.config_filter_status_combo_box)
        self.searchBooksButton.clicked.connect(self.search_books)

        self.config_filter_name_edit()
        self.config_filter_author_combo_box()
        self.config_filter_genre_combo_box()
        self.config_filter_status_combo_box()
        self.load_author_combo_box()
        self.load_genre_combo_box()

        self.bookListWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookListWidget.customContextMenuRequested.connect(self.show_book_list_widget_context_menu)

        if self.filterAuthorComboBox.count() == 0:
            self.filterAuthorCheckBox.setDisabled(True)
        if self.filterGenreComboBox.count() == 0:
            self.filterGenreCheckBox.setDisabled(True)

    def load_author_combo_box(self):
        self.filterAuthorComboBox.clear()
        self.filterAuthorComboBox.addItems(self.user_database_manager.get_user_authors())

    def load_genre_combo_box(self):
        self.filterGenreComboBox.clear()
        self.filterGenreComboBox.addItems(self.user_database_manager.get_user_genres())

    def show_book_searching(self):
        self.stackedWidget.setCurrentIndex(0)

    def config_filter_name_edit(self):
        self.filterNameEdit.setEnabled(self.filterNameCheckBox.isChecked())

    def config_filter_author_combo_box(self):
        self.filterAuthorComboBox.setEnabled(self.filterAuthorCheckBox.isChecked())

    def config_filter_genre_combo_box(self):
        self.filterGenreComboBox.setEnabled(self.filterGenreCheckBox.isChecked())

    def config_filter_status_combo_box(self):
        self.filterStatusComboBox.setEnabled(self.filterStatusCheckBox.isChecked())

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

    def update_book_list_widget_data(self):
        self.bookListWidget.clear()
        self.bookListWidget.addItems(map(lambda x: x[1], self.clue_book_data))

    def update_book_table_widget_data(self):
        pass

    def show_book_list_widget_context_menu(self, pos):
        menu = QMenu(self)
        editAction = QAction('Редактировать', self)
        deleteAction = QAction('Удалить', self)

        item = self.bookListWidget.itemAt(pos)
        if item is None:
            return

        editAction.triggered.connect(lambda: print('editing'))
        deleteAction.triggered.connect(lambda: print('deleting'))

        menu.addActions((editAction, deleteAction))
        menu.exec(self.bookListWidget.mapToGlobal(pos))

    def closeEvent(self, a0):
        self.user_database_manager.close()
