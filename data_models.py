from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def parse_date(value):
    """Parse a date string in '%Y-%m-%d' format to a date object.

    Args:
        value: A date string or None.

    Returns:
        A date object if value is a valid date string, otherwise None.
    """
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def parse_int(value):
    """Parse a value to an integer.

    Args:
        value: A value to convert to an integer.

    Returns:
        An integer if conversion is successful, otherwise None.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        """Return a developer-friendly string representation of the Author."""
        return f"Author({self.name}, {self.birth_date}, {self.date_of_death})"

    def __str__(self):
        """Return a human-readable string representation of the Author."""
        birth_date_str = (
            self.birth_date.strftime("%Y-%m-%d") if self.birth_date else "Unknown"
        )
        date_of_death_str = (
            self.date_of_death.strftime("%Y-%m-%d") if self.date_of_death else "Unknown"
        )
        return f"{self.name} ({birth_date_str}-{date_of_death_str})"

    @classmethod
    def validate(cls, form_data):
        errors = {}
        for column in cls.__table__.columns:
            if column.primary_key:
                continue

            if not column.nullable and not column.default:
                value = form_data.get(column.name).strip()
                if not value:
                    errors[column.name] = (
                        f"A non-empty {column.name.replace('_', ' ').title()} is required"
                    )

        return errors

    @classmethod
    def from_form(cls, form_data):
        """Create an Author instance from form data.

        Args:
            form_data: Dictionary containing 'name', 'birth_date', and 'date_of_death'.

        Returns:
            An Author instance with data from the form.
        """
        return cls(
            name=form_data.get("name"),
            birth_date=parse_date(form_data.get("birth_date")),
            date_of_death=parse_date(form_data.get("date_of_death")),
        )


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(100), nullable=False, unique=True)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)
    author = db.relationship("Author", backref="books")
    cover_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Book({self.isbn}, {self.title}, {self.publication_year}, {self.author_id})"

    def __str__(self):
        return f"{self.title} ({self.publication_year})"

    @classmethod
    def validate(cls, form_data):
        """Validate Book form data for required fields.

        Args:
            form_data: Dictionary of form data to validate.

        Returns:
            Dictionary of field names to error messages. Empty dict if no errors.
        """
        errors = {}
        for column in cls.__table__.columns:
            if column.primary_key:
                continue

            if not column.nullable and not column.default:
                value = form_data.get(column.name).strip()
                if not value:
                    errors[column.name] = (
                        f"{column.name.replace('_', ' ').title()} is required"
                    )

        return errors

    @classmethod
    def from_form(cls, form_data, cover_url: str | None = None):
        """Create a Book instance from form data.

        Args:
            form_data: Dictionary containing 'isbn', 'title', 'publication_year', and 'author_id'.
            cover_url: Optional URL for the book's cover image.

        Returns:
            A Book instance with data from the form.
        """
        return cls(
            isbn=(form_data.get("isbn") or "").strip(),
            title=form_data.get("title"),
            publication_year=parse_int(form_data.get("publication_year")),
            author_id=parse_int(form_data.get("author_id")),
            cover_url=cover_url,
        )
