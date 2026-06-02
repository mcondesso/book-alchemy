import os

from flask import Flask, request, render_template, redirect, url_for, flash
from sqlalchemy import func

from data_models import db, Author, Book
from isbn_api import fetch_open_library_book_cover_small


app = Flask(__name__)
# App Secret key necessary for the the flash mechanism to work
app.secret_key = os.environ.get("SECRET_KEY", "dev")

library_db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/library.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{library_db_path}"
db.init_app(app)


@app.route("/")
def home():
    sort_by = request.args.get("sort_by", "title") or "title"
    if sort_by == "author":
        books = (
            Book.query.join(Author)
            .options(db.joinedload(Book.author))
            .order_by(func.lower(Author.name), func.lower(Book.title))
            .all()
        )
    else:
        books = (
            Book.query.join(Author)
            .options(db.joinedload(Book.author))
            .order_by(func.lower(Book.title))
            .all()
        )

    return render_template("home.html", books=books, sort_by=sort_by)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Display the add-author form and create an author on submission."""
    if request.method == "POST":
        form = request.form
        errors = Author.validate(form)
        if errors:
            return render_template("add_author.html", errors=errors, form=form)

        author = Author.from_form(form)
        db.session.add(author)
        db.session.commit()

        flash("Author added successfully", "success")
        return redirect(url_for("home"))

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Display the add-book form and create a book on submission."""
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        form = request.form
        errors = Book.validate(form)
        if errors:
            return render_template(
                "add_book.html",
                errors=errors,
                form=form,
                authors=authors,
            )

        # fetch cover URL (if any) from Open Library using the ISBN
        isbn_value = (form.get("isbn") or "").strip()
        cover_url = fetch_open_library_book_cover_small(isbn_value)

        book = Book.from_form(form, cover_url=cover_url)
        db.session.add(book)
        db.session.commit()

        flash("Book added successfully", "success")
        return redirect(url_for("home"))

    return render_template("add_book.html", authors=authors)


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
