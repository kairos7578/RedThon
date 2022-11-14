from flask import Flask, redirect, render_template, request, session, flash
from flaskext.mysql import MySQL
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from redThon.pybo.forms import UserCreateForm
from pymysql.cursors import DictCursor
import os
import string, random
import json
import hashlib
#import win32api

app = Flask(__name__)

#류재범 추가: DB 연동
load_dotenv(verbose=True)

app.secret_key = os.getenv('REDTHON_SECRET_KEY') #세션 사용을 위한 시크릿 키 설정
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10) # 로그인 지속시간 설정 현재 10분

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv('REDTHON_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('REDTHON_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('REDTHON_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('REDTHON_DATABASE_HOST')
mysql.init_app(app)

#@app.route("/", methods=['GET', 'POST'])
#def root():
#    if request.method == 'GET':
#        return render_template("index.html")
#    else:
#        return render_template('test_image.html', title = "main")

@app.route("/", methods=['GET', 'POST'])
def root():
    print("로그인 상태 체크: %s" % (session_check()))
    if session_check():
        return render_template('test_image.html', title = "mainmap")
    else:
        return render_template("index.html")

@app.route("/mainmap")
def mainmap():
    return render_template('test_image.html', title = "mainmap")

@app.route("/cardstudy")
def cardstudy():
    return render_template('cardStudy.html', title = "mainmap")

@app.route("/header")
def header():
    return render_template('header.html', title = "header")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        username = request.form.get('username')
        userid = request.form.get('userid')
        password = request.form.get('password')
        quiz = request.form.get('quiz')
        age = request.form.get('age')

        db = mysql.connect()
        #유효성 검사
        cursor = db.cursor()
        cursor.execute("SELECT idx FROM member WHERE user_id = '%s'" % (userid))
        id_check = cursor.fetchone()
        if id_check is not None:
            flash("이미 가입한 아이디가 있습니다.")
            return redirect('/register')

        if username == "" or userid == "" or password == "" or quiz == "" or age == "":
            flash("모두 입력해주세요.")
            return redirect('/register')

        #회원가입
        cursor = db.cursor()
        cursor.execute("INSERT INTO member SET user_id = '%s', user_name = '%s', user_pw = md5('%s'), user_quiz = '%s', user_age = '%s', datetime = '%s'" % (userid, username, password, quiz, age, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()

        #확인
        cursor = db.cursor()
        cursor.execute("SELECT idx FROM member WHERE user_id = '%s' and user_pw = md5('%s')" % (userid, password))
        register_check = cursor.fetchone()
        if register_check is not None:
            flash("회원가입 성공")
            return redirect('/')
        else:
            flash("회원가입 실패")
            return redirect('/register')

@app.route("/idfind", methods=['GET', 'POST'])
def idfind():
    if request.method == 'GET':
        return render_template('id_find.html', title = "idfind")
    else:
        username = request.form.get('username')
        quiz = request.form.get('quiz')

        db = mysql.connect()

        #이름과 보물 1호로 아이디 서치
        cursor = db.cursor()
        cursor.execute("SELECT user_id FROM member WHERE user_name = '%s' and user_quiz = '%s'" % (username, quiz))
        find_check = cursor.fetchone()
        if find_check is not None:
            flash("아이디는 %s 입니다." % (find_check["user_id"]))
            return redirect("/")
        else:
            flash("아이디를 찾을 수 없습니다.")
            return redirect("/")
        #방법1)하나의 페이지 생성됨 > '되돌아기' 버튼 필요 -> 메인으로 이동 해야함...
        #방법2)하나의 페이지가 새로 띄워지는게 아니라, id_find.html페이지에서 밑에 "문구" 나타나는 형식으로 처리

    
@app.route("/pwfind", methods=['GET', 'POST'])
def pwfind():
    if request.method == 'GET':
        return render_template('pw_find.html', title = "pwfind")
    else:
        userid = request.form.get('userid')
        username = request.form.get('username')
        quiz = request.form.get('quiz')

        db = mysql.connect()

        #아이디와 이름과 보물 1호로 비밀번호 서치
        cursor = db.cursor()
        cursor.execute("SELECT user_pw FROM member WHERE user_id = '%s' and user_name = '%s' and user_quiz = '%s'" % (userid, username, quiz))
        find_check = cursor.fetchone()
        if find_check is not None:
            for i in range(123):
                pw = find_check["user_pw"].replace(hashlib.md5(chr(i).encode()).hexdigest(), chr(i))
            flash("비밀번호는 %s 입니다." % (pw))
            return redirect("/")
        else:
            flash("비밀번호를 찾을 수 없습니다.")
            return redirect("/")
        #방법1)하나의 페이지 생성됨 > '되돌아기' 버튼 필요 -> 메인으로 이동 해야함...
        #방법2)하나의 페이지가 새로 띄워지는게 아니라, id_find.html페이지에서 밑에 "문구" 나타나는 형식으로 처리



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    return render_template('auth/signup.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    userid = request.form.get('loginId')
    userpw = request.form.get('password')
    
    db = mysql.connect()
    #유효성 검사
    if userid == "" or userpw == "":
            flash("아이디와 비밀번호를 모두 입력해주세요.")
            return redirect('/')
    
    #로그인 시도
    cursor = db.cursor()
    cursor.execute("SELECT idx FROM member WHERE user_id = '%s' and user_pw = md5('%s')" % (userid, userpw))
    login_check = cursor.fetchone()
    if login_check is not None:
        flash("로그인 성공")
        #세션 설정 후 메인으로 이동
        letters_set = string.ascii_letters
        random_list = random.sample(letters_set,30)
        token_result = ''.join(random_list)
        print("랜덤 로그인 토큰: %s" % (token_result))

        cursor = db.cursor()
        cursor.execute("INSERT INTO session SET user_id = '%s', session = '%s', datetime = '%s'" % (userid, token_result, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()

        session["userId"] = userid
        session["loginToken"] = token_result

        return redirect('/')
    else:
        flash("로그인 실패(아이디 비번 불일치)")
        return redirect('/')

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('userId', None)
    session.pop('loginToken', None)
    return redirect('/')    

def session_check():
    if 'userId' in session and 'loginToken' in session:
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("SELECT idx FROM session WHERE user_id = '%s' and session = '%s'" % (session["userId"], session["loginToken"]))
        session_check = cursor.fetchone()
        if session_check is None:
            return 0
        else:
            return 1
    else:
        return 0

#def create_app() :
    #블루프린트
#    import auth_views
#    app.register_blueprint(auth_views.bp)
#    return app


