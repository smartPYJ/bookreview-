import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not ("postgres://postgres:splofic@localhost:5432/book_search"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(
    "postgres://postgres:splofic@localhost:5432/book_review")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

"""
@app.route("/login")
def login():
    return render_template("login.html")
"""

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/", methods=["Post"])
def loginuser():
    uname = request.form.get("username")
    passw = request.form.get("password")
 
    if db.execute("SELECT * FROM users WHERE username = :username  and password =:pass", {"username": uname, "pass": passw}).rowcount != 1:
        return render_template("index.html", message="Incorrect username or password.")
    else:
        user = db.execute("SELECT * FROM users WHERE username = :username  and password =:pass", {"username": uname, "pass": passw}).fetchone()
        session["user_id"] = user.user_id
        return render_template("search.html", message="Welcome ", user=session["user_id"])


@app.route("/register", methods=["POST"])
def registeruser():

    # Get form information.
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    password = request.form.get("password")
    country = request.form.get("country")
    username = request.form.get("username")

    # Add users to database .

    if db.execute("SELECT * FROM users WHERE username = :uname", {"uname": username}).rowcount >= 1:
        return render_template("error.html", message="Username already exixt.")

    db.execute("INSERT INTO users (firstname,lastname,email,password,country,username) VALUES (:fname, :lname, :email, :pass, :count, :uname)",
               {"fname": firstname, "lname": lastname, "email": email, "pass": password, "count": country, "uname": username})
    db.commit()
    return render_template("success.html", name=firstname, last=lastname)




@app.route("/search", methods=["GET","POST"])
def searchbooks(): 
    if request.method =="GET":
        return render_template("index.html", message="please login to search")
    
    else:
        keyword = request.form.get("search")
    
        find = str("%"+str(keyword)+"%")
        """return search for books ."""
        if str(keyword) == "":
            return render_template("search.html", message="Search field empty")
        elif str(keyword) != "":
            all_books = db.execute("SELECT * FROM books WHERE isbn LIKE :word OR  title LIKE  :word OR author LIKE :word", {"word": find}).fetchall()
            if len(all_books)>0:
                return render_template("search.html", all_books=all_books)
            else:
                return render_template("search.html", message=" Oop's.. sorry, No match found !!")
@app.route("/book/<int:book_id>")
def book(book_id):
   
    
    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such Book.")

    # Get all passengers.
    book_review = db.execute("SELECT * FROM review WHERE book_id = :book_id",
                            {"book_id": book_id}).fetchall()
    return render_template("book.html", book=book, reviews=book_review)

@app.route("/book", methods = ["POST"] )
def bookreview():
    name = request.form.get("name")
    review = request.form.get("review")
    rate = request.form.get("rate") 
    book_id = int(request.form.get("bookid") ) 
    
    db.execute("INSERT INTO review (book_id,review, user_id, rate) VALUES (:book_id, :review, :user, :rate)",
            {"book_id":book_id,  "review":review ,"user":session["user_id"], "rate":rate})
    db.commit()
    