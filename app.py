from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import time
import os
from helpers import login_required, datetimeformat, allowed_file
import requests

# Defining app settings
app = Flask(__name__)
db = SQL("sqlite:///socialme.db")

# Setting up API keys
OPENWEATHER = os.environ.get("OPENWEATHER")
if OPENWEATHER == None:
    raise Exception("No API key for OpenWeather set")

NEWS = os.environ.get("NEWS")
if NEWS == None:
    raise Exception("No API key for the news api set")

# Hardcoding the latitude and longitude for the weather
# Might want to make this dynamic in a later version
LAT = 49.815273
LON = 6.129583

# Defining upload folder
app.config["UPLOAD_FOLDER"] = "./static/public"

# Setting session up
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_NAME"] = "csocial"
Session(app)

# Defining filters
# Formats the date correctly
app.jinja_env.filters["datetimeformat"] = datetimeformat


@app.route("/")
def main():
    """
    This will generate the main feed and show the posts and comments.
    """
    id = session.get("user_id")
    if id == None:
        return redirect("/login")

    # Fetch the news feed
    logged_in = db.execute("SELECT * FROM users WHERE id = (?)", id)
    # Fetch user information

    user = db.execute("SELECT users.id, users.username, users.picture, post.id AS postid, post.author, post.text, post.timestamp FROM post JOIN users ON post.author = users.id ORDER BY timestamp DESC")

    comments = db.execute(
        "SELECT users.id, users.username, users.picture, post.id AS postid, COMMENTS.commentid, COMMENTS.userid AS commid, COMMENTS.commenttext, COMMENTS.timestamp FROM users JOIN COMMENTS ON users.id = COMMENTS.userid JOIN post ON COMMENTS.postid = post.id")

    # Fetch the news
    news = requests.get(
        f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS}")
    news = news.json()

    # Fetch the weather
    weather = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&units=metric&appid={OPENWEATHER}")
    weather = weather.json()

    # Render the main template
    return render_template("index.html", feed=user, news=news, weather=weather, user=logged_in, comments=comments)


@app.route("/checkuser/<username>")
def checkuser(username):
    """
    A small API to check if username is already tken
    """
    users = db.execute(
        "SELECT COUNT(*) FROM users WHERE username = (?)", username)
    users = users[0]["COUNT(*)"]

    # This returns a JSON
    return {"count": users}


@app.route("/checkmail/<email>")
def checkmail(email):
    """
    A small API to check if email is already tken
    """
    users = db.execute(
        "SELECT COUNT(*) FROM users WHERE email = (?)", email)
    users = users[0]["COUNT(*)"]

    # This returns a JSON
    return {"count": users}


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Display the registration form, or save the user in the database
    """
    if request.method == "GET":
        return render_template("Start/register.html")
    else:
        # Check for data integrity
        if not request.form.get("Username"):
            return render_template("error.html", error="warning", errormessage="Please enter a username")

        if not request.form.get("password"):
            return render_template("error.html", error="warning", errormessage="Please enter a password")

        if not request.form.get("confirmation"):
            return render_template("error.html", error="warning", errormessage="Please enter a password")

        if not request.form.get("email"):
            return render_template("error.html", error="warning", errormessage="Please enter a email")

        # Check if passwords are the same
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", error="warning", errormessage="Passwords don't match")

        # extract values
        username = request.form.get("Username")
        email = request.form.get("email")

        # Check if username is taken
        users = db.execute(
            "SELECT COUNT(*) FROM users WHERE username = (?)", username)

        if users[0]["COUNT(*)"] > 0:
            return render_template("error.html", error="warning", errormessage="Username is taken")

        # Check if email is taken
        users = db.execute(
            "SELECT COUNT(*) FROM users WHERE email = (?)", email)

        if users[0]["COUNT(*)"] > 0:
            return render_template("error.html", error="warning", errormessage="Email is taken")

        # Generate a password hash
        password = generate_password_hash(request.form.get("password"))

        #  save user into database
        data = db.execute("INSERT INTO users (username, hash, email, activated, picture) VALUES(?, ?, ?, ?, ?)",
                          username, password, email, "true", "empty.jpg")
        id = data

        # log the user in
        session["user_id"] = id

        # redirect to the main page
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Render login page or checks credentials
    """
    # Check if user is logged in and method is get, then render login form
    if request.method == "GET" and session.get("user_id") == None:
        return render_template("Start/login.html")

    # Check if user is logged in, then redirect him to home
    if session.get("user_id") != None:
        return redirect("/")

    # The only remaining case would be if the user sent a post request
    # Check data integrity
    if not request.form.get("email"):
        return render_template("error.html", error="warning", errormessage="Please enter an email")
    email = request.form.get("email")

    if not request.form.get("password"):
        return render_template("error.html", error="warning", errormessage="Please enter a password")
    password = request.form.get("password")

    # Check if user exists
    fetch = db.execute("SELECT * FROM users WHERE email = (?)", email)
    if len(fetch) != 1:
        return render_template("error.html", error="danger", errormessage="No such email address")

    # Check if password is correct
    if not check_password_hash(fetch[0]["hash"], password):
        return render_template("error.html", error="danger", errormessage="Wrong password")

    if fetch[0]["activated"] == "false":
        return render_template("error.html", error="danger", errormessage="You are banned from the plattform")
    # Log the user in
    session["user_id"] = fetch[0]["id"]

    # Redirect
    return redirect("/")


@app.route("/logout")
def logout():
    """
    Log the user out. This was taken over from the finance app.
    """

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        """
        Display the profile
        """
        # If there is no id set in the URL, display the profile of the logged in user
        # Since this has the decorator "login_required", we can assume the user is always logged in
        if not request.args.get("id"):
            id = session["user_id"]
        else:
            id = request.args.get("id")

        # Fetch all the posts the user did
        postings = db.execute(
            "SELECT *, post.id AS postid FROM post JOIN users ON post.author = users.id WHERE post.author = (?) ORDER BY timestamp DESC", id)

        # Fetch the comments
        comments = db.execute(
            "SELECT COMMENTS.postid, COMMENTS.userid, COMMENTS.timestamp, COMMENTS.commenttext, users.id, users.username, users.picture FROM COMMENTS JOIN post ON COMMENTS.postid = post.id JOIN users ON COMMENTS.userid = users.id ORDER BY COMMENTS.timestamp ASC")

        # Get profile information
        profile = db.execute("SELECT * FROM users WHERE id = (?)", id)

        # If we didn't find any user, return a blank profile
        if len(profile) == 0:
            profile = [{"username": "blank", "email": "blank", "empty": "yes"}]

        return render_template("Profile/profile.html", feed=postings, profile=profile, comments=comments)
    else:
        """
        Saving a new post
        """
        # Check for data integrity
        if not request.form.get("input"):
            return "Something went horribly wrong"

        if not request.form.get("text"):
            return "Enter a comment, you dummy!"

        input = request.form.get("input")

        # Check if it's a post or a comment
        if input == "post":
            timestamp = int(time.time())
            text = request.form.get("text")
            data = db.execute(
                "INSERT INTO post (author, timestamp, text) VALUES (?, ?, ?)", session["user_id"], timestamp, text)
        if not request.form.get("from"):
            return redirect("/profile")

        where = request.form.get("from")
        if where == "feed":
            return redirect("/")
        else:
            return redirect("/profile")


@ app.route("/comment", methods=["POST"])
@ login_required
def comment():
    # save the user id
    userid = session.get("user_id")


    # Check for data integritiy
    if not request.form.get("postid"):
        return render_template("error.html", error="warning", errormessage="An error occured, please try again.")

    if not request.form.get("comment"):
        return render_template("error.html", error="warning", errormessage="An error occured, please try again.")

    # Set the variables
    postid = request.form.get("postid")
    comment = request.form.get("comment")
    timestamp = int(time.time())

    # Save to database
    db.execute("INSERT INTO COMMENTS (postid, userid, commenttext, timestamp) VALUES (?, ?, ?, ?)",
               postid, userid, comment, timestamp)

    if not request.form.get("from"):
        return redirect("/")
    elif request.form.get("from") == "feed":
        return redirect("/")
    else:
        return redirect(f"/profile?id={request.form.get('from')}")


@app.route("/deletecomment", methods=["POST", "GET"])
@login_required
def deletecomment():
    if request.method != "POST":
        return redirect("/")

    # Check for the session id
    id = session.get("user_id")
    if id == None:
        return redirect("/")

    if not request.form.get("commentid"):
        if not request.form.get("from"):
            return redirect("/")

        if request.form.get("from") == "profile":
            return redirect(f"/profile=id?{request.form.get.id}")
        else:
            return redirect("/")
    # Delete the comment
    # First, check if the user can actually delete the comment
    commentid = request.form.get("commentid")
    data = db.execute(
        "SELECT * FROM COMMENTS WHERE commentid = (?)", commentid)

    # Check if the user is the author of the comment
    # If not, redirect the user where he came from
    if id != data[0]["userid"]:
        if not request.form.get("from"):
            return redirect("/")
        if request.form.get("from") == "profile":
            return redirect(f"/profile=id?{request.form.get.id}")
        else:
            return redirect("/")

    # Delete the comment from the database
    # then redirect the user where he came from
    db.execute("DELETE FROM COMMENTS WHERE commentid = (?)", commentid)
    if not request.form.get("from"):
        return redirect("/")
    if request.form.get("from") == "profile":
        return redirect(f"/profile=id?{request.form.get.id}")
    else:
        return redirect("/")


@app.route("/deletepost", methods=["POST", "GET"])
@login_required
def deletepost():
    if request.method != "POST":
        return redirect("/")

    # Check for a valid user id
    id = session.get("user_id")
    if id == None:
        return redirect("/")

    # Check for data integrity
    if not request.form.get("postid"):
        return render_template("error.html", error="warning", errormessage="Something went wrong.")

    postid = request.form.get("postid")

    # TODO Check if the session_idd is actually the author

    # Delete the posting from the database
    db.execute("DELETE FROM post WHERE id = (?)", postid)

    if not request.form.get("from"):
        return redirect("/")

    if not request.form.get("id"):
        return redirect("/")

    userid = request.form.get("id")

    where = request.form.get("from")
    if where == "profile":
        return redirect(f"/profile?id={userid}")
    else:
        return redirect("/profile")


@app.route("/settings", methods=["POST", "GET"])
@login_required
def settings():
    # If request method
    if request.method == "GET":
        # Get user data
        # This will work, since the user must be logged in, thus the user_id has
        # to be submitted
        id = session.get("user_id")
        data = db.execute("SELECT * FROM users WHERE ID = (?)", id)

        return render_template("Profile/settings.html", user=data)

    # else: post method

    # Fetch the current user settings
    id = session.get("user_id")
    data = db.execute("SELECT * FROM users WHERE ID = (?)", id)
    # Check for file integrity

    # if no file is submitted, we pass on an empty string
    if "file" in request.files:
        file = request.files["file"]
    else:
        file = data[0].picture

    # Check if username is not taken yet
    username = request.form.get("username")
    if not username:
        username = data[0]["username"]
    # Check if user wants to change his username
    if username != data[0]["username"]:
        # Check if username is taken
        usercount = checkuser(username)
        if usercount["count"] > 0:
            return render_template("error.html", error="error", errormessage="Username is taken")

    # check if new password is OK
    pass1 = request.form.get("password")
    pass2 = request.form.get("repeat")

    if not pass1 or not pass2:
        newpass = data[0]["hash"]

    if pass1 != pass2:
        return render_template("error.html", error="error", errormessage="Passwords don't match")
    if pass1 and pass2:
        newpass = generate_password_hash(pass1)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
    else:
        filename = data[0]["picture"]

    # Update the entry in the database

    # TODO check what to update
    db.execute("UPDATE users SET username = (?), hash = (?), picture = (?) WHERE id = (?)",
               username, newpass, filename, id)
    return redirect("/settings")
