from typing import Any, Sequence

from database.models import Book, Author, Genre, UserAuthorLink, UserGenreLink
from sqlalchemy import create_engine, select, Row
from sqlalchemy.orm import sessionmaker


class UserDatabaseManager:
    def __init__(self, user_id):
        self.user_id = user_id
        engine = create_engine('sqlite:///database/books_db.sqlite')
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()

    def get_user_authors(self) -> tuple[Any, ...]:
        statement = select(Author.title).select_from(Author).join(UserAuthorLink).where(
            UserAuthorLink.UserId == int(self.user_id))
        return tuple(map(lambda x: x[0], self.session.execute(statement).all()))

    def get_user_genres(self) -> tuple[Any, ...]:
        statement = select(Genre.title).select_from(Genre).join(UserGenreLink).where(
            UserGenreLink.UserId == int(self.user_id))
        return tuple(map(lambda x: x[0], self.session.execute(statement).all()))

    def search_books(self, title=None, author=None, genre=None, status=None, sort_by=None) -> Sequence[
        Row[tuple[Any, Any, Any, Any, Any]]]:
        sort_dict = {'Названию': Book.title, 'Автору': Author.title}

        statement = select(Book.BookId, Book.title, Author.title, Genre.title, Book.status).select_from(Book).where(
            Book.user_id_book_fk == int(self.user_id)).join(Author).join(Genre)

        if title is not None:
            statement = statement.where(Book.title.like(f'%{title}%'))
        if author is not None:
            statement = statement.where(Author.title == str(author))
        if genre is not None:
            statement = statement.where(Genre.title == str(genre))
        if status is not None:
            statement = statement.where(Book.status == str(status))
        statement = statement.order_by(sort_dict[sort_by])

        return self.session.execute(statement).all()
