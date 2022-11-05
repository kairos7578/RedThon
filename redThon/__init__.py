from flask import Flask, redirect, render_template, request
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os
from redThon.pybo.forms import UserCreateForm
import win32api

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        return render_template('test_image.html', title = "main")

@app.route("/mainmap")
def mainmap():
    return render_template('test_image.html', title = "mainmap")

@app.route("/header")
def header():
    return render_template('header.html', title = "header")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        userid = request.form.get('userid') 
        return redirect('/')

@app.route("/idfind", methods=['GET', 'POST'])
def idfind():
    if request.method == 'GET':
        return render_template('id_find.html', title = "idfind")
    else:
        return "아이디는 0000 입니다." #방법1)하나의 페이지 생성됨 > '되돌아기' 버튼 필요 -> 메인으로 이동 해야함...
                                      #방법2)하나의 페이지가 새로 띄워지는게 아니라, id_find.html페이지에서 밑에 "문구" 나타나는 형식으로 처리

    
@app.route("/pwfind", methods=['GET', 'POST'])
def pwfind():
    if request.method == 'GET':
        return render_template('pw_find.html', title = "pwfind")
    else:
        return "비밀번호는 0000 입니다." #방법1)하나의 페이지 생성됨 > '되돌아기' 버튼 필요 -> 메인으로 이동 해야함...
                                        #방법2)하나의 페이지가 새로 띄워지는게 아니라, id_find.html페이지에서 밑에 "문구" 나타나는 형식으로 처리



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