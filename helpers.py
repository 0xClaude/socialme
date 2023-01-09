from functools import wraps
from flask import session
from datetime import datetime, timezone

# Defining allowed pictures for profile picture
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def login_required(f):
    """
    Decorate routes to require login.
    This was taken from the cs50 finance app.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def datetimeformat(value):
    """
    Format the date correctly
    """
    date = datetime.fromtimestamp(value)
    return date.strftime("%d %b %Y, %H:%M")


def round(value):
    """
    Rounds the temperature
    """
    return "{0:0.1f}".format(round(value))


def allowed_file(filename):
    """
    Check if the file submitted can be uploaded
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
