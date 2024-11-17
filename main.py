import sys

import qdarktheme
from LoginWindow import LoginWindow
from MainMenu import MainMenu
from PyQt6.QtWidgets import QApplication


class AppManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_user_id = None

        # engine = create_engine('sqlite:///books_db.sqlite')
        # Base = declarative_base()
        # Base.metadata.create_all(engine)

    def run(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()
        self.app.exec()

    def show_main_menu(self, user_id):
        self.login_window.close()
        self.main_menu = MainMenu(self, user_id)
        self.main_menu.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # qdarktheme.setup_theme()
    # ex = LoginWindow()
    # ex.show()
    # sys.excepthook = except_hook
    # sys.exit(app.exec())

    app_manager = AppManager()
    qdarktheme.setup_theme()
    sys.excepthook = except_hook
    app_manager.run()

    # engine = create_engine('sqlite:///database/books_db.sqlite')
    # Session = sessionmaker(bind=engine)
    #
    # session = Session()
    #
    # # record = session.query(models.User).get({})
    # # print(record)
    # # new_record = session.query(models.User).all()
    # # print(*map(lambda user: user.password, new_record))
    #
    # statement = select(models.User.UserId, models.User.username).where(models.User.UserId == 45)
    #
    # result = session.execute(statement)
    #
    # print(*result, sep='\n')
    #
    # # session.commit()
    # # session.delete(record)
    # # session.commit()
    # #
    # # session.close()
    #
    # # engine = create_engine('sqlite:///database/books_db.sqlite')
    # # Session = sessionmaker(bind=engine)
    # #
    # # session = Session()
    # #
    # # for _ in range(100):
    # #     new_user = models.User(username=f'User{_}', password='1234')
    # #
    # #     session.add(new_user)
    # # session.commit()
    # #
    # # session.close()

    # engine = create_engine('sqlite:///database/books_db.sqlite')
    # Session = sessionmaker(bind=engine)
    #
    # session = Session()
    #
    # session.commit()
    # session.close()

    pass
