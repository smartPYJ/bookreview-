import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://postgres:splofic@localhost:5432/book_review")
db = scoped_session(sessionmaker(bind=engine))


def main():
    count = 0
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        count +=1
    print(
        f" A total of {count} was added into the Database.")
    db.commit()


if __name__ == "__main__":
    main()
