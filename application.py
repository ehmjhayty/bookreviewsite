import os
import requests

from flask import Flask, session, render_template,request,redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import app, User, BookAuthorAssoc, Book, Author, Review
from helper import login_required

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")




# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def search(search_type,search_text):
    ''' function to search books based on the search type (isbn,title,author) the user
        chose.

        returns a list object.
    '''

    book = []

    if search_type == 'isbn':
        print('isbn')
        book = BookAuthorAssoc.get_by_isbn(search_text)

    elif search_type == 'title':
        book = Book.get_by_title(search_text)
        print(type(book))

    elif search_type == 'author':
        book = Author.get_by_author(search_text)

    return book

@app.route("/", methods=["POST", "GET"])
def index():
    '''
     The home page of the website which renders index template
     except that when there is a search input, it redirects to
     the book function
    '''

    user = session.get('user_id')
    if request.args.get("submit"):
        search_type = request.args.get('searchType')
        search_text = request.args.get('searchText')

        return redirect(url_for('book', type=search_type, text=search_text))

    return render_template('index.html', user=user)

@app.route("/login/", methods=["POST", "GET"])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username,password)
        user = user.is_present()
        if(user):
            #Create a session once user is found on the database
            session['user_id'] = user.user_id
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route("/signup/", methods=["POST"])
def signup():
    username = request.form['username']
    password = request.form['password']
    if username and password:
        user = User(username,password)

        #Check if the input username already does not exist on the database
        if (not user.user_exist()):
            #save the user the database if it has unique username
            #user.create_user()
            #database is full, don't create a user for now!
            pass

    return redirect(url_for('index'))

@app.route("/logout/", methods=["POST","GET"])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route("/home/", methods=["POST", "GET"])
@login_required
def home():
    return render_template('home.html', name='home')




@app.route("/book/<type>/<text>", methods=["POST", "GET"])
def book(type, text):
    '''
     book function receives two parameters from the search input,
     the search type (author,title,isbn) and text to be searched

     renders the search results
    '''

    user = session.get('user_id')
    book = search(type,text)

    return render_template('book.html', book=book, text=text, user=user)

@app.route("/about/", methods = ["GET"])
def about():
    user = session.get("user_id")
    return render_template('about.html', user=user)


@app.route("/home/<isbn>")
#@login_required
def book_page(isbn):
    '''
        Displays information such as title,isbn and author of a book
        average rating and number of ratings are also but they are taken from an api
        not on the database
    '''

    user = session.get('user_id')
    api = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": '27gOLxYgKYkVUkr6gnY4Aw', "isbns": isbn})
    api_data = dict(api.json()['books'][0])
    book = BookAuthorAssoc.get_by_isbn(isbn)

    #Book reviews are not available yet due to database limit
    #reviews = Review.get_book_review(isbn)

    return render_template('bookpage.html', book=book, data=api_data, user=user)

@app.route("/review/<isbn>", methods=["POST"])
#@login_required
def review(isbn):
    '''
        Submits review for a book
    '''
    if request.method == 'POST':
        user_id = session["user_id"]
        review_text = request.form['text']
        rate = request.form['rate']
        review = Review(isbn, user_id, review_text, rate)
        #review.create_review()

        return redirect(url_for('book_page', isbn=isbn))

