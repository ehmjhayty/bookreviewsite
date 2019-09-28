from flask import Flask
from flask_sqlalchemy import SQLAlchemy


SQLALCHEMY_TRACK_MODIFICATIONS = False
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dtgpwtmiyxcpge:4f9ab372bc36d3d916ac8a380a2e603aaeac6d1bd1d015e7d6bc9e39b63b3168@ec2-54-227-245-146.compute-1.amazonaws.com:5432/d9tebt8afsmuoo'

db = SQLAlchemy(app)


class Book(db.Model):
    __tablename__ = 'book'
    isbn = db.Column(db.String(15), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    author = db.relationship('Author', secondary='bookauthorassoc')
    review = db.relationship('Review', backref=db.backref('books', lazy=True))

    def __init__ (self, isbn, title,year):
        self.isbn = isbn
        self.title = title
        self.year = year

    def get_by_title(text):
        book = []
        book_list = Book.query.filter(Book.title.ilike("%"+text+"%")).limit(10).all()
        for item in book_list:
            book.extend(BookAuthorAssoc.get_by_isbn(item.isbn))

        return book



class Author(db.Model):
    __tablename__ = 'author'
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(110), nullable=False)

    book = db.relationship('Book', secondary='bookauthorassoc')

    def __init__(self, name):
        self.name = name

    def get_by_author(text):
        book = []
        book_list = Author.query.filter(Author.name.ilike("%"+text+"%")).limit(10).all()
        for item in book_list:
            book.append(BookAuthorAssoc.get_by_author(item.author_id))

        return book
    '''
    def save_author(self):
        db.session.add(self)
        db.session.commit()
    '''


class BookAuthorAssoc(db.Model):
    __tablename__ = 'bookauthorassoc'
    __table_args__ = (
        db.PrimaryKeyConstraint('isbn', 'author_id'),
    )
    isbn = db.Column(db.String(15), db.ForeignKey('book.isbn'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'))

    book = db.relationship('Book', backref=db.backref('bookauthorassoc'))
    author = db.relationship('Author', backref=db.backref('bookauthorassoc'))

    def __init__(self, isbn,author_id):
        self.isbn = isbn
        self.author_id = author_id

    def get_by_isbn(text):
        return BookAuthorAssoc.query.filter(BookAuthorAssoc.isbn.ilike("%"+text+"%")).limit(10).all()

    def get_by_author(text):
        return BookAuthorAssoc.query.filter_by(author_id=text).first()

class Review(db.Model):
    __tablename__ = 'review'
    __table_args__ = (
        db.PrimaryKeyConstraint('isbn', 'user_id'),
    )
    isbn = db.Column(db.String(15), db.ForeignKey('book.isbn'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    text = db.Column(db.Text,nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

    def __init__(self,isbn,user_id,text,rating):
        self.isbn = isbn
        self.user_id = user_id
        self.text = text
        self.rating = rating

    def create_review(self):
        present = Review.query.filter_by(isbn=self.isbn, user_id=self.user_id).first()

        if present is None:
            print("Present is none! I can save the book!")
            db.session.add(self)
            db.session.commit()

    def get_book_review(isbn):
        review = Review.query.filter_by(isbn=isbn).options(db.load_only('text')).all()
        return  review


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)

    def __init__(self, username,password):
        self.username = username
        self.password = password

    def is_present(self):
        return self.query.filter_by(username=self.username, password=self.password).first()

    def user_exist(self):
        return self.query.filter_by(username=self.username).first()

    def create_user(self):
        db.session.add(self)
        db.session.commit()