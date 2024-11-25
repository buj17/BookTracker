"""Классы-модели таблиц в базе данных, реализованные на SQLAlchemy"""
import os

from sqlalchemy import Column, Integer, Text, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base

_current_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_current_dir, 'books_db.sqlite')
ENGINE = create_engine(f'sqlite:///{_db_path}')
_Base = declarative_base()


class User(_Base):
    """Модель таблицы для пользователей"""
    __tablename__ = 'users'

    UserId = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)

    genres = relationship('Genre', secondary='user_genre_links', backref='users', lazy=True)
    authors = relationship('Author', secondary='user_author_links', backref='users', lazy=True)
    books = relationship('Book', backref='users', lazy=True)


class Genre(_Base):
    """Модель таблицы для жанров"""
    __tablename__ = 'genres'

    GenreId = Column(Integer, primary_key=True)
    title = Column(Text)


class Author(_Base):
    """Модель таблицы для авторов"""
    __tablename__ = 'authors'

    AuthorId = Column(Integer, primary_key=True)
    title = Column(Text)


class UserGenreLink(_Base):
    """Модель связующей таблицы жанров и пользователей, организующей связь многие ко многим
    Данная таблица нужна для того, чтобы у каждого пользователя был собственный набор жанров"""
    __tablename__ = 'user_genre_links'

    UserId = Column(Integer, ForeignKey('users.UserId'), primary_key=True)
    GenreId = Column(Integer, ForeignKey('genres.GenreId'), primary_key=True)


class UserAuthorLink(_Base):
    """Модель связующей таблицы авторов и пользователей, организующей связь многие ко многим
    Данная таблица нужна для того, чтобы у каждого пользователя был собственный набор авторов"""
    __tablename__ = 'user_author_links'

    UserId = Column(Integer, ForeignKey('users.UserId'), primary_key=True)
    AuthorId = Column(Integer, ForeignKey('authors.AuthorId'), primary_key=True)


class Book(_Base):
    """Модель таблицы для книг"""
    __tablename__ = 'books'

    BookId = Column(Integer, primary_key=True)
    title = Column(Text)
    author_id_book_fk = Column(Integer, ForeignKey('authors.AuthorId'))
    genre_id_book_fk = Column(Integer, ForeignKey('genres.GenreId'))
    status = Column(Text)
    user_id_book_fk = Column(Integer, ForeignKey('users.UserId'))


# Создаем базу данных при ее отсутствии
_Base.metadata.create_all(ENGINE)
