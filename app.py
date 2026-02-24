from flask import Flask, redirect
import os

app = Flask(__name__)

@app.route("/")
def home():
    return redirect("/screener")

@app.route("/screener")
def screener():
    try:
        with open("top500.csv.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        content = f"Error: {e}"

    return f"<pre>{content}</pre>"
