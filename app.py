from flask import Flask, render_template, url_for, request, redirect, session
import hashlib
import mysql.connector

# Make connection to database on client request
# so that data updates each request, rather than having to restart flask

app = Flask(__name__)
app.secret_key = "thisIsMySecretKeyPlsDontLeak"

# Last topic topic clicked on in case of GET redirect
lastTopicName = 0
lastClaimName = None
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
            "SELECT topic.topic, user.username, topic.dateCreated from topic join user on topic.createdBy=user.userID;")
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
            # Set the session variables
            session["username"] = username
            session["password"] = password

            # Get user admin status and set it in session variable
            query = "SELECT isAdmin FROM user WHERE user.username=%s"
            cursor.execute(query, (username, ))
            reply = cursor.fetchall()
            isAdmin = str(reply[0]).strip("(),")
            session["admin"] = isAdmin

            # Redirect user
            return redirect(request.referrer)

        else:
            return redirect(request.referrer)

    else:
        # If they try to get the login page then just redirect them to the home page.
        return redirect(request.referrer)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    # Set up database connection and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Check if the username already exists

        password = hashlib.sha256(password.encode())
        password = password.hexdigest()
        # Build using query for security
        query = "INSERT INTO user (username, password) VALUES (%s,%s)"
        cursor.execute(query, (username, password))
        conn.commit()
        return username + " | " + str(password)
    else:
        return redirect(request.referrer)


@app.route("/signout", methods=["GET"])
def signout():
    # If the username is there remove it
    session.pop("username", None)
    session.pop("password", None)
    session.pop("admin", None)

    # redirect to home page
    return redirect(request.referrer)


@app.route("/newtopic", methods=["GET"])
def newtopic():
    # If the user isnt logged in then tell them
    # TODO Create propper page
    if "username" not in session:
        return "Please Login"
    else:
        return render_template("newTopic.html")


@app.route("/deletetopic", methods=["POST"])
def deletetopic():
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # Checkf if session username is actually an admin
    query = "SELECT isAdmin FROM user WHERE user.username=%s"
    cursor.execute(query, (session["username"], ))
    reply = cursor.fetchall()

    topic = request.form["topic"]

    # Remove leading whitespace
    topic = topic[1:]

    if str(reply[0]).strip("(),") == "1":
        # Remove the topic
        query = 'DELETE FROM topic WHERE topic.topic=%s;'
        cursor.execute(
            query, (topic, ))
        conn.commit()
        return redirect("/")
    else:
        return "NOT ADMIN"


@app.route("/deleteclaim", methods=["POST"])
def deleteclaim():
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # Checkf if session username is actually an admin
    query = "SELECT isAdmin FROM user WHERE user.username=%s"
    cursor.execute(query, (session["username"], ))
    reply = cursor.fetchall()

    claim = request.form["claim"]

    # Remove leading whitespace
    claim = claim[1:]

    if str(reply[0]).strip("(),") == "1":
        # Remove the topic
        query = 'DELETE FROM claims WHERE claims.content=%s;'
        cursor.execute(
            query, (claim, ))
        conn.commit()
        return redirect("/claims")
    else:
        return "NOT ADMIN"


@app.route("/deletereply", methods=["POST"])
def deletereply():
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # Checkf if session username is actually an admin
    query = "SELECT isAdmin FROM user WHERE user.username=%s"
    cursor.execute(query, (session["username"], ))
    reply = cursor.fetchall()

    claimReply = request.form["reply"]

    # Remove leading whitespace
    claimReply = claimReply[1:]

    if str(reply[0]).strip("(),") == "1":
        # Remove the topic
        query = 'DELETE FROM replies WHERE replies.reply=%s;'
        cursor.execute(
            query, (claimReply, ))
        conn.commit()
        return redirect("/replies")
    else:
        return "NOT ADMIN"


@ app.route("/newclaim", methods=["GET"])
def newClaim():
    global lastTopicName
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # If the user isnt logged in then tell them
    # TODO Create propper page
    if "username" not in session:
        return "Please Login"
    else:
        # Get all claims for the topic selected
        query = "SELECT claims.content FROM claims where claims.topicID=(SELECT topicID from topic WHERE topic=%s)"
        cursor.execute(query, (lastTopicName, ))
        reply = cursor.fetchall()
        for i in range(0, len(reply)):
            reply[i] = str(reply[i]).strip("()',")

        return render_template("newClaim.html", claims=reply)


@ app.route("/newreply", methods=["GET"])
def newreply():
    global lastClaimName
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # If the user isnt logged in then tell them
    # TODO Create propper page
    if "username" not in session:
        return "Please Login"
    else:

        # Get all replies on the claim
        query = "SELECT replies.reply FROM replies where replies.claimID=(SELECT claimID FROM claims WHERE claims.content=%s)"
        cursor.execute(query, (lastClaimName, ))
        reply = cursor.fetchall()

        if not reply:
            return render_template("newReply.html", claim=lastClaimName)

        for i in range(0, len(reply)):
            reply[i] = str(reply[i]).strip("(),'")

        # Pass in the claim so can check if is replying to claim or to reply
        return render_template("newReply.html", claim=lastClaimName, replies=reply)


@ app.route("/createtopic", methods=["POST"])
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

        # Check if topic already exists
        query = "SELECT topicID FROM topic where topic.topic=%s"
        cursor.execute(query, (topic, ))
        reply = cursor.fetchall()

        if reply:
            return "Topic already exists"

        #
        # Build query for security, then execute command
        # TODO Add current date to topic
        query = 'INSERT INTO topic(topic, createdBy, dateCreated) VALUES (%s, (SELECT userID FROM user WHERE username=%s), CURDATE());'
        cursor.execute(query, (topic, username))
        conn.commit()

        # Redirect user back to home page
        return redirect("/")


@ app.route("/createclaim", methods=["POST"])
def createclaim():
    global lastTopicName
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    # If there is no logged in user then dont post topic
    if "username" not in session:
        return "You need to be logged in"
    else:

        claim = request.form["claim"]
        relationship = request.form["relationship"]
        selectedClaim = request.form["selectedClaim"]
        username = session["username"]

        # Check if claim already exists with same content.
        query = "SELECT claimID FROM claims where claims.content=%s"
        cursor.execute(query, (claim, ))
        reply = cursor.fetchall()

        if reply:
            return "Claim Already Exists"

        # Build query for security, then execute command
        # Insert claim into table
        query = 'INSERT INTO claims(content, userID, dateCreated, relationship, topicID) VALUES (%s, (SELECT userID FROM user WHERE username=%s), CURDATE(), %s, (SELECT topicID from topic WHERE topic=%s))'
        cursor.execute(
            query, (claim, username, relationship, str(lastTopicName)))
        conn.commit()

        # If a claim doesnt have a relationship then dont carry on
        if relationship == "none" or claim == "none":
            return redirect("/claims")

        # Get claims id that has just been made
        query = "SELECT claimID FROM claims where claims.content=%s"
        cursor.execute(query, (claim, ))
        reply = cursor.fetchall()
        claimID = str(reply[0]).strip("(),")

        # Get claim id of the relationship the user wants to make
        query = "SELECT claimID FROM claims where claims.content=%s"
        cursor.execute(query, (selectedClaim, ))
        reply = cursor.fetchall()
        claimRelation = str(reply[0]).strip("(),")

        # Insert relationship into table
        # Use claim Relation
        query = 'INSERT INTO claims_relation(claimOneID, claimTwoID, relation) VALUES (%s, %s, %s)'
        cursor.execute(
            query, (claimID, claimRelation, relationship))
        conn.commit()
        # Redirect user back to home page
        return redirect("/claims")


@ app.route("/createreply", methods=["POST"])
def createreply():
    global lastClaimName
    # Set Up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()
    cursor = conn.cursor(buffered=True)

    # If there is no logged in user then dont post topic
    if "username" not in session:
        return "You need to be logged in"
    else:
        # Get all post data
        replyContent = request.form["reply"]
        replyTo = request.form["replyTo"]
        relationship = request.form["relationship"]
        username = session["username"]

        # Check if reply already exists
        query = "SELECT replyID FROM replies where replies.reply=%s"
        cursor.execute(query, (replyContent, ))
        reply = cursor.fetchall()

        if reply:
            return "Reply Already Exists"

        # Check if replying to claim or reply.
        replyTo = str(replyTo).split("'")[1::2]
        toReplyID = str(replyTo[0])
        toReplyID = str(toReplyID)

        if replyTo[1] == "claim":
            # Insert reply into table
            query = 'INSERT INTO Replies(userID, claimID, reply, relation) VALUES ((SELECT userID from user where user.username=%s), (SELECT claims.claimID from claims WHERE claims.content=%s), %s, %s);'
            cursor.execute(query, (username,
                                   toReplyID, replyContent, relationship))
            conn.commit()

        elif replyTo[1] == "reply":
            # Cannot modify a table you select from in the same statement
            query = 'SELECT replyID FROM replies WHERE replies.reply=%s;'
            cursor.execute(query, (toReplyID, ))
            reply = cursor.fetchall()
            toReplyID = str(reply[0]).strip("(),")
            query = "SELECT claimID FROM claims where claims.content=%s"
            cursor.execute(query, (lastClaimName, ))
            reply = cursor.fetchall()
            claimID = str(reply[0]).strip("(),")

            # Insert reply into table
            query = 'INSERT INTO Replies(userID, claimID, reply, relation, toReplyID) VALUES ((SELECT userID FROM user where user.username=%s), %s, %s, %s, %s);'
            cursor.execute(query, (username, claimID,
                                   replyContent, relationship, toReplyID))
            conn.commit()

        return redirect("/replies")


@ app.route("/claims", methods=["GET", "POST"])
def claims():
    global lastTopicName
    if request.method == "POST":

        # Set Up connection to db and cursor
        conn = mysql.connector.connect(
            user="root", password="root", host="127.0.0.1", database="forum")
        cursor = conn.cursor()

        # Get the topic name they clicked on
        topicName = request.form["topicData"]

        # Get the topicID from the name in the db
        query = "SELECT topic.topicID FROM topic where topic.topic=%s;"
        cursor.execute(query, (topicName, ))
        reply = cursor.fetchall()
        topicID = str(reply[0]).replace(",", '')
        topicID = topicID.strip("()")

        # Get all claims for this topicID
        query = "SELECT claims.content, user.username, dateCreated FROM claims INNER JOIN user ON claims.userID=user.userID WHERE claims.topicID=%s;"
        cursor.execute(query, (topicID, ))
        claimData = cursor.fetchall()

        # Set last topic to use for redirect
        lastTopicName = request.form["topicData"]

        return render_template('claims.html', claimData=claimData, data=request.form["topicData"], session=session)

    if request.method == "GET":

        # Set Up connection to db and cursor
        conn = mysql.connector.connect(
            user="root", password="root", host="127.0.0.1", database="forum")
        cursor = conn.cursor()

        # If the last topic name hasnt been set
        if lastTopicName == None:
            return redirect("/")
        else:
            # Otherwise use the lastTopicName to get all the claims

            # Get the topicID from the name in the db
            query = "SELECT topic.topicID FROM topic where topic.topic=%s;"
            cursor.execute(query, (lastTopicName, ))
            reply = cursor.fetchall()
            topicID = str(reply[0]).replace(",", '')
            topicID = topicID.strip("()")

            # Get all claims for this topicID
            query = "SELECT claims.content, user.username, claims.dateCreated FROM claims INNER JOIN user ON claims.userID=user.userID WHERE claims.topicID=%s;"
            cursor.execute(query, (topicID, ))
            claimData = cursor.fetchall()
            return render_template('claims.html', claimData=claimData, session=session)


@ app.route("/replies", methods=["GET", "POST"])
def replies():
    global lastClaimName
    # Set up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()

    if request.method == "POST":
        # Get the claim name they clicked on
        claimName = request.form["claimData"]

        # Get the claimID from the claim content in the db
        query = "SELECT Claims.claimID FROM Claims where Claims.content=%s;"
        cursor.execute(query, (claimName, ))
        reply = cursor.fetchall()
        claimID = str(reply[0]).replace(",", '')
        claimID = claimID.strip("()")

        # Get all replies for this claimID
        query = "SELECT Replies.replyID, Replies.reply, user.username, Replies.toReplyID, Replies.relation FROM Replies INNER JOIN user ON replies.userID=user.userID WHERE replies.claimID=%s;"
        cursor.execute(query, (claimID, ))
        replyData = cursor.fetchall()

        # Get all claim relations for this claim id
        query = "SELECT claims_relation.claimOneID, claims_relation.claimTwoID, claims_relation.relation, claims.content FROM claims_relation INNER JOIN claims on claims_relation.claimOneID=claims.claimID OR claims_relation.claimTwoID=claims.claimID WHERE claims_relation.claimOneID=%s OR claims_relation.claimTwoID=%s;"
        cursor.execute(query, (claimID, claimID))
        relationData = cursor.fetchall()
        found = []

        for s in relationData:
            if claimName not in s:
                found.append(s)

        print("_______________-" + str(found))
        # Set last claim to use for get redirect
        lastClaimName = request.form["claimData"]
        return render_template('replies.html', replyData=replyData, claimContent=claimName, relationData=found, session=session)

    if request.method == "GET":
        claimName = lastClaimName

        # Get the claimID from the claim content in the db
        query = "SELECT Claims.claimID FROM Claims where Claims.content=%s;"
        cursor.execute(query, (claimName, ))
        reply = cursor.fetchall()
        claimID = str(reply[0]).replace(",", '')
        claimID = claimID.strip("()")

        # Get all replies for this claimID
        query = "SELECT Replies.replyID, Replies.reply, user.username, Replies.toReplyID, Replies.relation FROM Replies INNER JOIN user ON replies.userID=user.userID WHERE replies.claimID=%s;"
        cursor.execute(query, (claimID, ))
        replyData = cursor.fetchall()

        return render_template('replies.html', replyData=replyData, claimContent=claimName, session=session)


@app.route("/search", methods=["POST"])
def search():
    # Set up connection to db and cursor
    conn = mysql.connector.connect(
        user="root", password="root", host="127.0.0.1", database="forum")
    cursor = conn.cursor()
    if request.method == "POST":

        # Get what the user wants to search for
        search = request.form["searchBar"]

        # Get all topics with the same string
        query = "SELECT topic.topic, user.username, topic.dateCreated from topic join user on topic.createdBy=user.userID WHERE topic.topic=%s;"
        cursor.execute(query, (search, ))
        topicSearchData = cursor.fetchall()

        # Get all claims with the same string
        query = "SELECT claims.content, user.username, dateCreated FROM claims INNER JOIN user ON claims.userID=user.userID WHERE claims.content=%s;"
        cursor.execute(query, (search, ))
        claimSearchData = cursor.fetchall()

        return render_template("search.html", topicSearchData=topicSearchData, claimSearchData=claimSearchData, session=session)


if (__name__) == "__main__":
    app.run(debug=True, TEMPLATES_AUTO_RELOAD=True)
