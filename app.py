from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector

conn = mysql.connector.connect(
    user="root", password="root", host="127.0.0.1", database="forum")
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = "thisIsMySecretKeyPlsDontLeak"

# TODO Check if user is logged in using session
@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        return request.form["password"]

    else:
        cursor.execute(
            "SELECT topic.topic, user.username from topic join user on topic.createdBy=user.userID;")
        topicData = cursor.fetchall()
        return render_template('index.html', topicData=topicData)


# Could just not include GET as a method and it wont load the page, only allowing posts to /login
@app.route("/login", methods=["POST", "GET"])
def login():
    # If method is POST then login the user
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # password = hash(password) #NEED TO REPLACE HASH
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
            return session["username"] + session["password"]

        else:
            return "NO USERS FOUND"

    else:
        # If they try to get the login page then just redirect them to the home page.
        return redirect("/")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # password = hash(password) #REPLACE

        # Build using query for security
        query = "INSERT INTO user (username, password) VALUES (%s,%s)"
        cursor.execute(query, (username, password))
        conn.commit()
        return username + " | " + str(password)
    else:
        return redirect("/")


if (__name__) == "__main__":
    app.run(debug=True, TEMPLATES_AUTO_RELOAD=True)
