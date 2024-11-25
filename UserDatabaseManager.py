"""Реализация взаимодействия с базой данных"""

import csv
from typing import Any, Sequence

from database.models import Book, Author, Genre, UserAuthorLink, UserGenreLink
from sqlalchemy import create_engine, select, update, delete, Row, and_
from sqlalchemy.orm import sessionmaker


class GenreInUseError(Exception):
    """При попытке удалить жанр, который есть среди книг пользователя вызывается данное исключение"""


class AuthorInUseError(Exception):
    """При попытке удалить автора, который есть среди книг пользователя вызывается данное исключение"""


class CsvImportError(Exception):
    """При ошибке импортирования csv вызывается данное исключение"""


class UserDatabaseManager:
    """Основной класс для взаимодействия с базой данных"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        engine = create_engine('sqlite:///database/books_db.sqlite')
        session_maker = sessionmaker(bind=engine)
        self.session = session_maker()

    def commit(self):
        """Фиксирование изменений в базе данных"""
        self.session.commit()

    def close(self):
        """Закрытие подключения к базе данных"""
        self.session.close()

    def rollback(self):
        """Отмена изменений, если при работе с базой данных произошло исключение"""
        self.session.rollback()

    def get_user_authors(self) -> tuple[tuple, ...]:
        """Возвращает кортеж, каждый элемент которого - кортеж с названием автора и его ИД"""
        statement = select(Author.title, Author.AuthorId).select_from(Author).join(UserAuthorLink).where(
            UserAuthorLink.UserId == int(self.user_id))
        return tuple(map(tuple, self.session.execute(statement).all()))

    def get_user_genres(self) -> tuple[tuple, ...]:
        """Возвращает кортеж, каждый элемент которого - кортеж с названием жанра и его ИД"""
        statement = select(Genre.title, Genre.GenreId).select_from(Genre).join(UserGenreLink).where(
            UserGenreLink.UserId == int(self.user_id))
        return tuple(map(tuple, self.session.execute(statement).all()))

    def search_books(self, title: str | None = None,
                     author: str | None = None,
                     genre: str | None = None,
                     status: str | None = None,
                     sort_by: str | None = None) -> Sequence[Row[tuple[Any, Any, Any, Any, Any]]]:
        """Возвращает информацию о книгах, подходящих по фильтрам и отсортированных по автору или названию"""
        sort_dict = {'Названию': Book.title, 'Автору': Author.title}

        statement = select(Book.BookId, Book.title, Author.title, Genre.title, Book.status).select_from(Book).where(
            Book.user_id_book_fk == self.user_id).join(Author).join(Genre)

        if title is not None:
            statement = statement.where(Book.title.like(f'%{title.lower()}%'))
        if author is not None:
            statement = statement.where(Author.title == str(author.lower()))
        if genre is not None:
            statement = statement.where(Genre.title == str(genre.lower()))
        if status is not None:
            statement = statement.where(Book.status == str(status))
        statement = statement.order_by(sort_dict[sort_by])

        return self.session.execute(statement).all()

    def search_genres(self, title: str) -> Sequence[Row[tuple[Any, Any]]]:
        """Возвращает информацию о жанрах, название которых содержит title"""
        statement = select(Genre.GenreId, Genre.title).select_from(Genre).where(
            and_(UserGenreLink.UserId == self.user_id, Genre.title.like(f'%{title.lower()}%'))).join(
            UserGenreLink).order_by(Genre.title)
        return self.session.execute(statement).all()

    def search_authors(self, title: str) -> Sequence[Row[tuple[Any, Any]]]:
        """Возвращает информацию об авторах, название которых содержит title"""
        statement = select(Author.AuthorId, Author.title).select_from(Author).where(
            and_(UserAuthorLink.UserId == self.user_id, Author.title.like(f'%{title.lower()}%'))).join(
            UserAuthorLink).order_by(Author.title)
        return self.session.execute(statement).all()

    def get_genre(self, genre_id: int) -> str:
        """Возвращает название жанра по его ИД"""
        statement = select(Genre.title).select_from(Genre).where(Genre.GenreId == genre_id)
        return self.session.execute(statement).first()[0]

    def get_author(self, author_id: int) -> str:
        """Возвращает название автора по его ИД"""
        statement = select(Author.title).select_from(Author).where(Author.AuthorId == author_id)
        return self.session.execute(statement).first()[0]

    def get_book(self, book_id: int) -> Row[tuple[Any, Any, Any, Any]]:
        """Возвращает информацию о книге по его ИД"""
        statement = select(Book.title, Author.title, Genre.title, Book.status).select_from(Book).where(
            Book.BookId == book_id).join(Author).join(Genre)
        return self.session.execute(statement).first()

    def add_genre(self, title: str):
        """Добавление жанра с названием title
        Если данного жанра нет в таблице жанров, то добавляется новый жанр с названием title и берется его ИД;
        Если данный жанр есть в таблице жанров, то берется ИД жанра с названием title;
        После этого в таблицу user_genre_links добавляется запись с ИД пользователя и ИД жанра"""
        statement = select(Genre.GenreId).select_from(Genre).where(Genre.title == title.lower())
        genre_id = self.session.execute(statement).first()
        if genre_id is None:
            new_genre = Genre(title=title.lower())
            self.session.add(new_genre)
            self.commit()
            genre_id = new_genre.GenreId
        else:
            genre_id = genre_id[0]

        new_user_genre_link = UserGenreLink(UserId=self.user_id, GenreId=genre_id)
        self.session.add(new_user_genre_link)
        self.commit()

    def edit_genre(self, genre_id: int, title: str):
        """Редактирование жанра с ИД genre_id: старое название заменяется на title;
        Если жанра с новым названием нет в таблице жанров, то добавляется новый жанр с названием title и берется его ИД;
        Если данный жанр есть в таблице жанров, то берется ИД жанра с названием title;
        После этого в таблицу user_genre_links добавляется запись с ИД пользователя и ИД жанра"""
        find_genre_statement = select(Genre.GenreId).select_from(Genre).where(Genre.title == title)
        new_genre_id = self.session.execute(find_genre_statement).first()
        if new_genre_id is None:
            new_genre = Genre(title=title.lower())
            self.session.add(new_genre)
            self.commit()
            new_genre_id = new_genre.GenreId
        else:
            new_genre_id = new_genre_id[0]

        update_user_genre_link_statement = update(UserGenreLink).where(
            and_(UserGenreLink.GenreId == genre_id, UserGenreLink.UserId == self.user_id)).values(GenreId=new_genre_id)
        self.session.execute(update_user_genre_link_statement)
        self.commit()

    def delete_genre(self, genre_id: int):
        """Удаление из таблицы user_genre_links записи, где ИД жанра - genre_id"""
        find_genre_statement = select(Book.genre_id_book_fk).select_from(Book).where(
            and_(Book.genre_id_book_fk == genre_id, Book.user_id_book_fk == self.user_id))
        result = self.session.execute(find_genre_statement).first()
        if result is not None:
            raise GenreInUseError

        delete_genre_statement = delete(UserGenreLink).where(and_(UserGenreLink.GenreId == genre_id,
                                                                  UserGenreLink.UserId == self.user_id))
        self.session.execute(delete_genre_statement)
        self.commit()

    def add_author(self, title: str):
        """Добавление автора с названием title
        Если данного автора нет в таблице жанров, то добавляется новый автор с названием title и берется его ИД;
        Если данный автор есть в таблице жанров, то берется ИД автора с названием title;
        После этого в таблицу user_author_links добавляется запись с ИД пользователя и ИД автора"""
        statement = select(Author.AuthorId).select_from(Author).where(Author.title == title.lower())
        author_id = self.session.execute(statement).first()
        if author_id is None:
            new_author = Author(title=title.lower())
            self.session.add(new_author)
            self.commit()
            author_id = new_author.AuthorId
        else:
            author_id = author_id[0]

        new_user_author_link = UserAuthorLink(UserId=self.user_id, AuthorId=author_id)
        self.session.add(new_user_author_link)
        self.commit()

    def edit_author(self, author_id: int, title: str):
        """Редактирование автора с ИД author_id: старое название заменяется на title;
        Если автора с новым названием нет в таблице авторов,
        то добавляется новый автор с названием title и берется его ИД;
        Если данный жанр есть в таблице жанров, то берется ИД жанра с названием title;
        После этого в таблицу user_genre_links добавляется запись с ИД пользователя и ИД жанра"""
        find_author_statement = select(Author.AuthorId).select_from(Author).where(Author.title == title)
        new_author_id = self.session.execute(find_author_statement).first()
        if new_author_id is None:
            new_author = Author(title=title.lower())
            self.session.add(new_author)
            self.commit()
            new_author_id = new_author.AuthorId
        else:
            new_author_id = new_author_id[0]

        update_user_author_link_statement = update(UserAuthorLink).where(
            and_(UserAuthorLink.AuthorId == author_id, UserAuthorLink.UserId == self.user_id)).values(
            AuthorId=new_author_id)
        self.session.execute(update_user_author_link_statement)
        self.commit()

    def delete_author(self, author_id: int):
        """Удаление из таблицы user_author_links записи, где ИД автора - author_id"""

        find_author_statement = select(Book.author_id_book_fk).select_from(Book).where(
            and_(Book.author_id_book_fk == author_id, Book.user_id_book_fk == self.user_id))
        result = self.session.execute(find_author_statement).first()
        if result is not None:
            raise AuthorInUseError

        delete_author_statement = delete(UserAuthorLink).where(and_(UserAuthorLink.AuthorId == author_id,
                                                                    UserAuthorLink.UserId == self.user_id))
        self.session.execute(delete_author_statement)
        self.commit()

    def add_book(self, title: str, author_id_book_fk: int, genre_id_book_fk: int, status: str):
        """Добавление книги"""
        new_book = Book(title=title.lower(), author_id_book_fk=author_id_book_fk, genre_id_book_fk=genre_id_book_fk,
                        status=status, user_id_book_fk=self.user_id)
        self.session.add(new_book)
        self.commit()

    def edit_book(self, book_id: int, title: str, author_id_book_fk: int, genre_id_book_fk: int, status: str):
        """Редактирование книги"""
        statement = update(Book).where(Book.BookId == book_id).values(title=title.lower(),
                                                                      author_id_book_fk=author_id_book_fk,
                                                                      genre_id_book_fk=genre_id_book_fk,
                                                                      status=status)
        self.session.execute(statement)
        self.commit()

    def delete_book(self, book_id: int):
        """Удаление книги"""
        statement = delete(Book).where(Book.BookId == book_id)
        self.session.execute(statement)
        self.commit()

    def export_csv(self, filename: str):
        """Экспорт книг в формате csv;
        Создается файл filename и в него записывается информация о книгах (без указания пользователя)"""
        statement = select(Book.title, Author.title, Genre.title, Book.status).select_from(Book).where(
            Book.user_id_book_fk == self.user_id).join(Author).join(Genre)

        user_book_data = self.session.execute(statement).all()
        header = ('Book', 'Author', 'Genre', 'Status')
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(user_book_data)

    def import_csv(self, filename: str):
        """Импорт книг в формате csv;
        Стирается вся информация о жанрах, авторах и книгах пользователя;
        При чтении каждой записи добавляется жанр / автор при их отсутствии;
        Добавляется книга"""
        self.clear_all_user_data()

        with open(filename, encoding='utf-8') as file:
            author_dict, genre_dict = {}, {}

            reader = csv.DictReader(file)
            for record in reader:
                record: dict
                author_title: str = record['Author'].lower()
                if author_title not in author_dict:
                    self.add_author(author_title)
                get_authorid_statement = select(Author.AuthorId).select_from(Author).where(Author.title == author_title)
                author_id = self.session.execute(get_authorid_statement).one()[0]
                author_dict[author_title] = author_id

                genre_title: str = record['Genre'].lower()
                if genre_title not in genre_dict:
                    self.add_genre(record['Genre'])
                get_genre_id_statement = select(Genre.GenreId).select_from(Genre).where(Genre.title == genre_title)
                genre_id = self.session.execute(get_genre_id_statement).one()[0]
                genre_dict[genre_title] = genre_id

                self.add_book(record['Book'], author_dict[author_title], genre_dict[genre_title], record['Status'])

    def clear_all_user_data(self):
        """Удаление всех книг, авторов и жанров пользователя"""
        clear_books_statement = delete(Book).where(Book.user_id_book_fk == self.user_id)
        clear_user_genre_links = delete(UserGenreLink).where(UserGenreLink.UserId == self.user_id)
        clear_user_author_links = delete(UserAuthorLink).where(UserAuthorLink.UserId == self.user_id)

        self.session.execute(clear_books_statement)
        self.session.execute(clear_user_genre_links)
        self.session.execute(clear_user_author_links)

        self.commit()
