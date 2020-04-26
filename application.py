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


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/loginuser", methods=["Post"])
def loginuser():
    uname = request.form.get("username")
    passw = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username  and password =:pass", {"username": uname, "pass": passw}).rowcount == 1:
        return render_template("search.html", message="Welcome ", user=uname)

    return render_template("login.html", message="Incorrect username or password.")


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


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/search", methods=["POST"])
def searchbooks(): 
    keyword = request.form.get("search")
    while True:
       
        find = str("%"+str(keyword)+"%")
        """return search for books ."""
        if str(keyword) == "":
            return render_template("search.html", message="No Match found")
        else:
            all_books = db.execute("SELECT * FROM books WHERE isbn LIKE :word OR  title LIKE  :word OR author LIKE :word", {"word": find}).fetchall()
            return render_template("search.html", all_books=all_books)
          
       