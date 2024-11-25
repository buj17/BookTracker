"""Реализация окна для входа в аккаунт"""
from PyQt6.QtWidgets import QWidget
from database.models import User, ENGINE
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from ui import LoginWindow_ui


class LoginWindow(QWidget, LoginWindow_ui.Ui_Form):
    """Окно для входа в аккаунт"""

    def __init__(self, app_manager):
        super().__init__()
        self.setupUi(self)
        self.app_manager = app_manager
        session_maker = sessionmaker(bind=ENGINE)
        self.session = session_maker()

        self.login_errorLabel.setStyleSheet('color: red')
        self.signUp_errorLabel.setStyleSheet('color: red')

        self.loginButton.clicked.connect(self.login)
        self.signUpButton.clicked.connect(self.register_user)

    def login(self):
        """Слот для входа в аккаунт"""
        username, password = self.login_usernameEdit.text(), self.login_passwordEdit.text()

        statement = select(User.username, User.password, User.UserId).select_from(User).where(
            User.username == f'{username}')
        record = self.session.execute(statement).first()

        if record is None:
            self.login_errorLabel.setText('Неверное имя пользователя или пароль')
        else:
            clue_username, clue_password, user_id = record
            if clue_username == username and clue_password == password:
                user = self.session.query(User).filter(User.UserId == f'{user_id}').first()
                self.login_errorLabel.setText('')
                self.app_manager.show_main_menu(user.UserId)
            else:
                self.login_errorLabel.setText('Неверное имя пользователя или пароль')

    def register_user(self):
        """Слот для регистрации"""
        username = self.signUp_usernameEdit.text()
        password = self.signUp_passwordEdit.text()

        if username == '':
            self.signUp_errorLabel.setText('Имя пользователя не может быть пустым')
            return
        if password == '':
            self.signUp_errorLabel.setText('Введите пароль')
            return
        if password != self.signUp_repeatPasswordEdit.text():
            self.signUp_errorLabel.setText('Введенные пароли не совпадают')
            return

        statement = select(User.username).select_from(User).where(User.username == f'{username}')
        existing_username = self.session.execute(statement).first()

        if existing_username is None:
            new_user = User(username=username, password=password)
            self.session.add(new_user)
            self.session.commit()
            self.signUp_errorLabel.setText('')
            self.app_manager.show_main_menu(new_user.UserId)
        else:
            self.signUp_errorLabel.setText('Пользователь с таким именем уже существует')

    def closeEvent(self, a0):
        """При закрытии окна закрывается подключение к базе данных"""
        self.session.close()
