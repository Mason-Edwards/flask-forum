from flask import Flask, render_template, url_for, request, redirect
import mysql.connector

conn = mysql.connector.connect(
    user="root", password="root", host="127.0.0.1", database="forum")
cursor = conn.cursor()

app = Flask(__name__)


@app.route('/')
def index():
    cursor.execute(
        "SELECT topic.topic, user.username from topic join user on topic.createdBy=user.userID;")
    topicData = cursor.fetchall()

    for(topic) in topicData:
        print(topic)
    return render_template('index.html', topicData=topicData)


if (__name__) == "__main__":
    app.run(debug=True, TEMPLATES_AUTO_RELOAD=True)
