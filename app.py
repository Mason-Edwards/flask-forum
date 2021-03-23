from flask import Flask, render_template, url_for, request, redirect, session
import hashlib
import mysql.connector

# Make connection to database on client request
# so that data updates each request, rather than having to restart flask

app = Flask(__name__)
app.secret_key = "thisIsMySecretKeyPlsDontLeak"

# TODO Check if user is logged in using session


@app.route('/', methods=["POST", "GET"])
def index():
    # Set ip database connection and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    if request.method == "POST":
        return request.form["password"]

    else:
        cursor.execute(
            "SELECT topic.topic, user.username from topic join user on topic.createdBy=user.userID;")
        topicData = cursor.fetchall()
        return render_template('index.html', topicData=topicData, session=session)


# Could just not include GET as a method and it wont load the page, only allowing posts to /login
@app.route("/login", methods=["POST", "GET"])
def login():
    # Set up database connection and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # If method is POST then login the user
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password = hashlib.sha256(password.encode())
        password = password.hexdigest()
        # Query db
        cursor.execute('SELECT * FROM user WHERE username="' +
                       username + '" AND password="' + str(password) + '";')
        reply = cursor.fetchall()

        # If the query has a result
        if reply:
            for(user) in reply:
                print(user)

            # Set the session variables
            session["username"] = username
            session["password"] = password

            # Redirect user
            return redirect("/")

        else:
            return "NO USERS FOUND"

    else:
        # If they try to get the login page then just redirect them to the home page.
        return redirect("/")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    # Set up database connection and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password = hashlib.sha256(password.encode())
        password = password.hexdigest()
        # Build using query for security
        query = "INSERT INTO user (username, password) VALUES (%s,%s)"
        cursor.execute(query, (username, password))
        conn.commit()
        return username + " | " + str(password)
    else:
        return redirect("/")


@app.route("/signout", methods=["GET"])
def signout():
    # If the username is there remove it
    session.pop("username", None)

    # redirect to home page
    return redirect("/")


@app.route("/newtopic", methods=["GET"])
def newtopic():
    # If the user isnt logged in then tell them
    # TODO Create propper page
    if "username" not in session:
        return "Please Login"
    else:
        return render_template("newTopic.html")


@app.route("/createtopic", methods=["POST"])
def createtopic():
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # If there is no logged in user then dont post topic
    if "username" not in session:
        return "You need to be logged in"
    else:
        topic = request.form["topic"]
        username = session["username"]
        #
        # Build query for security, then execute command
        query = 'INSERT INTO topic(topic, createdBy) VALUES (%s, (SELECT userID FROM user WHERE username=%s))'
        cursor.execute(query, (topic, username))
        conn.commit()

        # Redirect user back to home page
        return redirect("/")


if (__name__) == "__main__":
    app.run(debug=True, TEMPLATES_AUTO_RELOAD=True)
