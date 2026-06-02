import urllib.request
import urllib.error


def fetch_open_library_book_cover_small(isbn: str) -> str | None:
    """Return Open Library small cover URL for an ISBN if available, otherwise None.

    Uses the Open Library Covers API and verifies the URL with a HEAD request.
    Returns the image URL (jpg) or None when not found or on network errors.
    """
    if not isbn:
        return None

    isbn_clean = isbn.replace("-", "").replace(" ", "")
    url = f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-S.jpg"

    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if getattr(resp, "status", None) == 200:
                return url
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        return None

    return None
