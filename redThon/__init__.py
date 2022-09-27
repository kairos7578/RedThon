from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def root():
    return render_template('index.html', title = "main")

@app.route("/header")
def header():
    return render_template('header.html', title = "header")
