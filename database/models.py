import os

from sqlalchemy import Column, Integer, Text, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'books_db.sqlite')
engine = create_engine(f'sqlite:///{db_path}')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    UserId = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)

    genres = relationship('Genre', secondary='user_genre_links', backref='users', lazy=True)
    authors = relationship('Author', secondary='user_author_links', backref='users', lazy=True)
    books = relationship('Book', backref='users', lazy=True)


class Genre(Base):
    __tablename__ = 'genres'

    GenreId = Column(Integer, primary_key=True)
    title = Column(Text)

    # users = relationship('User', secondary='user_genre_links', backref='genres', lazy=True)


class Author(Base):
    __tablename__ = 'authors'

    AuthorId = Column(Integer, primary_key=True)
    title = Column(Text)

    # users = relationship('User', secondary='user_author_links', backref='authors', lazy=True)


class UserGenreLink(Base):
    __tablename__ = 'user_genre_links'

    UserId = Column(Integer, ForeignKey('users.UserId'), primary_key=True)
    GenreId = Column(Integer, ForeignKey('genres.GenreId'), primary_key=True)


class UserAuthorLink(Base):
    __tablename__ = 'user_author_links'

    UserId = Column(Integer, ForeignKey('users.UserId'), primary_key=True)
    AuthorId = Column(Integer, ForeignKey('authors.AuthorId'), primary_key=True)


class Book(Base):
    __tablename__ = 'books'

    BookId = Column(Integer, primary_key=True)
    title = Column(Text)
    author_id_book_fk = Column(Integer, ForeignKey('authors.AuthorId'))
    genre_id_book_fk = Column(Integer, ForeignKey('genres.GenreId'))
    status = Column(Text)
    user_id_book_fk = Column(Integer, ForeignKey('users.UserId'))

    # users = relationship('User', backref='books', lazy=True)
    # authors = relationship('Author', backref='books', lazy=True)
    # genres = relationship('Genre', backref='books', lazy=True)


Base.metadata.create_all(engine)
