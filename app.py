import os
from pathlib import Path

from flask import Flask, request, render_template, redirect, url_for, flash
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book
from isbn_api import fetch_open_library_book_cover_small


app = Flask(__name__)
# App Secret key necessary for the the flash mechanism to work
app.secret_key = os.environ.get("SECRET_KEY", "dev")

library_db_path = Path(__file__).resolve().parent / "data" / "library.sqlite"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{library_db_path}"
db.init_app(app)


@app.route("/")
def home():
    """Display the home page with a list of books, optionally filtered and sorted."""
    sort_by = request.args.get("sort_by", "title") or "title"
    search_query = (request.args.get("q") or "").strip()

    books_query = Book.query.join(Author).options(db.joinedload(Book.author))
    if search_query:
        search_pattern = f"%{search_query}%"
        books_query = books_query.filter(
            or_(
                Book.title.ilike(search_pattern),
                Author.name.ilike(search_pattern),
                Book.isbn.ilike(search_pattern),
            )
        )

    if sort_by == "author":
        books = books_query.order_by(
            func.lower(Author.name), func.lower(Book.title)
        ).all()
    else:
        books = books_query.order_by(func.lower(Book.title)).all()

    return render_template(
        "home.html",
        books=books,
        sort_by=sort_by,
        search_query=search_query,
    )


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
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            if "UNIQUE constraint failed: authors.name" in str(exc):
                flash("An author with that name already exists.", "error")
            else:
                flash("Unable to add author due to a database error.", "error")
            return render_template("add_author.html", form=form)

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
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            if "UNIQUE constraint failed: books.isbn" in str(exc):
                flash("A book with this ISBN already exists.", "error")
            else:
                flash("Unable to add book due to a database error.", "error")
            return render_template(
                "add_book.html",
                form=form,
                authors=authors,
            )

        flash("Book added successfully", "success")
        return redirect(url_for("home"))

    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["DELETE", "POST"])
def delete_book(book_id):
    """Delete a book and remove its author if they have no remaining books."""
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id
    author_name = book.author.name
    book_title = book.title

    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author_id).count()
    if remaining_books == 0:
        author = Author.query.get(author_id)
        if author:
            db.session.delete(author)
            db.session.commit()
            flash(
                f"Book '{book_title}' deleted and author '{author_name}'"
                " removed because they had no other books.",
                "success",
            )
            return redirect(url_for("home"))

    flash(f"Book '{book_title}' deleted successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
