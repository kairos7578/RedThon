from flask import Flask, redirect, render_template, request
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os
from redThon.pybo.forms import UserCreateForm

app = Flask(__name__)

@app.route("/")
def root():
    return render_template('index.html', title = "main")

@app.route("/mainmap")
def mainmap():
    return render_template('test_image.html', title = "mainmap")

@app.route("/header")
def header():
    return render_template('header.html', title = "header")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        print("여기111")
        return render_template("register.html")
    else:
        return redirect('/')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    return render_template('auth/signup.html', form=form)


#def create_app() :
    #블루프린트
#    import auth_views
#    app.register_blueprint(auth_views.bp)
#    return app


#류재범 추가: DB 연동
load_dotenv(verbose=True)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv('REDTHON_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('REDTHON_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('REDTHON_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('REDTHON_DATABASE_HOST')
mysql.init_app(app)

db = mysql.connect()
cursor = db.cursor();
cursor.execute("SELECT * FROM test_table WHERE 1")
connect_test = cursor.fetchone()
print(connect_test)