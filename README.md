# Book Alchemy

A simple Flask library application for managing books and authors with SQLite storage and web forms.

## Features

- **Add authors** – Create new authors with name and optional birth/death dates
- **Add books** – Add books with title, ISBN, publication year, and author
- **Search books** – Search by title, author name, or ISBN from the home page
- **Delete books** – Remove books directly from the library homepage
- **Author cleanup** – Automatically delete an author if they have no remaining books
- **Cover lookup** – Fetch small book cover images from Open Library when a book is added
- **Flask templates** – Render HTML views using Jinja2 templates

## Setup

1. Clone the repository
2. Create and activate a Python virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python app.py
```

Open your browser at `http://127.0.0.1:5000` and use the site to:
- Add new authors and books
- Search the library by title, author, or ISBN
- Delete books from the homepage
- Automatically remove authors with no remaining books
