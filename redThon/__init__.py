from flask import Flask, redirect, render_template, request, session, flash
from flaskext.mysql import MySQL
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from redThon.pybo.forms import UserCreateForm
from pymysql.cursors import DictCursor
import os
import string, random
import json

app = Flask(__name__)

#류재범 추가: DB 연동
load_dotenv(verbose=True)

app.secret_key = os.getenv('REDTHON_SECRET_KEY') #세션 사용을 위한 시크릿 키 설정
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=100) # 로그인 지속시간 설정 현재 100분

mysql = MySQL(cursorclass=DictCursor)
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

        #스테이지 정보 가져오기
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM clear_stage WHERE user_id = '%s'" % (session["userId"]))
        cs = cursor.fetchone()
        return render_template('test_image.html', title = "mainmap", clear_stage = cs)
    else:
        return render_template("index.html")

@app.route("/clear", methods=['GET', 'POST'])
def clear():
    #request.args.get("stage", 0)
    #DB에 저장하기

    #DB 검색
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clear_stage WHERE user_id = '%s'" % (session["userId"]))
    m = cursor.fetchone()
    if m is not None:
        #UPDATE
        cursor2 = db.cursor()
        cursor2.execute("UPDATE clear_stage SET stage%s = 1 WHERE user_id = '%s'" % (request.args.get("stage", 0), session["userId"]))
        db.commit()
    else:
        #INSERT
        cursor2 = db.cursor()
        cursor2.execute("INSERT INTO clear_stage SET user_id = '%s', stage%s = 1" % (session["userId"], request.args.get("stage", 0)))
        db.commit()

    return redirect('/')

@app.route("/mainmap")
def mainmap():
    return render_template('test_image.html', title = "mainmap")

@app.route("/cardstudy")
def cardstudy():
    #print(request.args["stage"])
    #스테이지 따라문제 카드 가져오기
    if(request.args["stage"] != "" and request.args["stage"] is not None):
        print("문제 함수 들어옴")
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM card WHERE card_level = '%s' ORDER BY card_temp asc" % (request.args["stage"]))
        card = cursor.fetchall()

        for row in card:
            if(row['card_type'] == 2):
                #문제카드 있으면 가져오기
                cursor2 = db.cursor()
                cursor2.execute("SELECT * FROM card_back_problem WHERE card_no = '%s'" % (row["idx"]))
                cp = cursor2.fetchall()
                row.update(card_problem=cp)

            #앞장 설명 이미지 가져오기
            cursor6 = db.cursor()
            cursor6.execute("SELECT * FROM card_front_image WHERE card_num = '%s'" % (row["idx"]))
            fci = cursor6.fetchall()
            row.update(card_front_image=fci)

            #뒷장 설명 이미지 가져오기
            cursor4 = db.cursor()
            cursor4.execute("SELECT * FROM card_back_image WHERE card_num = '%s'" % (row["idx"]))
            bci = cursor4.fetchall()
            row.update(card_back_image=bci)

            #추가 설명 이미지 가져오기
            cursor3 = db.cursor()
            cursor3.execute("SELECT * FROM card_image WHERE card_num = '%s'" % (row["idx"]))
            ci = cursor3.fetchall()
            row.update(card_image=ci)

            #북마크 있는지 체크
            cursor5 = db.cursor()
            cursor5.execute("SELECT card_no FROM bookmark WHERE user_id = '%s' and card_no = '%s'" % (session["userId"], row["idx"]))
            bk = cursor5.fetchone()
            if bk is not None:
                row.update(bookmark='on')
            else:
                row.update(bookmark='off')
    return render_template('cardStudy.html', title = "mainmap", card=card, temp_ck = request.args.get("temp", 0))

@app.route("/bookmark_add", methods=['GET', 'POST'])
def bookmark_add():
    #세션 체크
    if session_check():
        db = mysql.connect()
        #이미 북마크가 있는지 검색
        bookmark_ck = db.cursor()
        bookmark_ck.execute("SELECT card_no FROM bookmark WHERE user_id = '%s' and card_no = '%s'" % (session["userId"], request.args["card_no"]))
        ckck = bookmark_ck.fetchone()
        print(ckck)
        if ckck is not None:
            #북마크가 있으므로 제거
            db = mysql.connect()
            cursor = db.cursor()
            cursor.execute("DELETE FROM bookmark WHERE user_id = '%s' and card_no = '%s'" % (session["userId"], request.args["card_no"]))
            db.commit()
            return "DELETE"
        else:
            #북마크 추가
            db = mysql.connect()
            cursor = db.cursor()
            cursor.execute("INSERT INTO bookmark SET user_id = '%s', card_no = '%s'" % (session["userId"], request.args["card_no"]))
            db.commit()
            return "ADD"
    else:
        return "FAIL"

@app.route("/bookmark_load", methods=['GET', 'POST'])
def bookmark_load():
    #북마크 모두 가져오기
    if session_check():
        db = mysql.connect()
        #이미 북마크가 있는지 검색
        bookmark_load = db.cursor()
        bookmark_load.execute("SELECT card_no FROM bookmark WHERE user_id = '%s'" % (session["userId"]))
        bl = bookmark_load.fetchall()
        for row in bl:
            #위치 가져오기 포맷 ex: 1-5, 2,8, 7-5...
            card_load = db.cursor()
            card_load.execute("SELECT * FROM card WHERE idx = '%s'" % (row["card_no"]))
            cl = card_load.fetchone()
            row.update(card=cl)
        return bl
    else:
        return "FAIL"

@app.route("/bookmark")
def bookmark():
    #print(request.args["stage"])
    #스테이지 따라문제 카드 가져오기
    if(request.args["stage"] != "" and request.args["stage"] is not None):
        print("문제 함수 들어옴")
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM card WHERE card_level = '%s' ORDER BY card_temp asc" % (request.args["stage"]))
        card = cursor.fetchall()
        for row in card:
            if(row['card_type'] == 2):
                #문제카드 있으면 가져오기
                cursor2 = db.cursor()
                cursor2.execute("SELECT * FROM card_back_problem WHERE card_no = '%s'" % (row["idx"]))
                cp = cursor2.fetchall()
                row.update(card_problem=cp)

            #뒷장 설명 이미지 가져오기
            cursor4 = db.cursor()
            cursor4.execute("SELECT * FROM card_back_image WHERE card_num = '%s'" % (row["idx"]))
            bci = cursor4.fetchall()
            row.update(card_back_image=bci)

            #추가 설명 이미지 가져오기
            cursor3 = db.cursor()
            cursor3.execute("SELECT * FROM card_image WHERE card_num = '%s'" % (row["idx"]))
            ci = cursor3.fetchall()
            row.update(card_image=ci)

        """
        cursor = db.cursor()
                cursor.execute("SELECT * FROM card_back_problem WHERE card_no = '%s'" % (row["idx"]))
                card_problem = cursor.fetchall()
                for row2 in card_problem:
                    print(row2["card_content"])
        """

    return render_template('bookmark.html', title = "bookmark", card=card)

@app.route("/finalStudy1")
def finalStudy1():
    return render_template('finalStudy1.html', title = "final1")

@app.route("/finalStudy2")
def finalStudy2():
    return render_template('finalStudy2.html', title = "final2")

@app.route("/finalStudy3")
def finalStudy3():
    return render_template('finalStudy3.html', title = "final2")

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
        if session_check():
            return redirect('/')
        else:
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
        if session_check():
            return redirect('/')
        else:
            return render_template('pw_find.html', title = "idfind")
    else:
        userid = request.form.get('userid')
        username = request.form.get('username')
        quiz = request.form.get('quiz')
        password = request.form.get('password')

        db = mysql.connect()

        #아이디와 이름과 보물 1호로 비밀번호 서치
        cursor = db.cursor()
        cursor.execute("SELECT user_pw FROM member WHERE user_id = '%s' and user_name = '%s' and user_quiz = '%s'" % (userid, username, quiz))
        find_check = cursor.fetchone()
        if find_check is not None:
            #류재범 수정
            # 비밀번호 찾기 -> 변경으로 수정
            cursor = db.cursor()
            cursor.execute("UPDATE member SET user_pw = md5('%s') WHERE user_id = '%s' and user_name = '%s' and user_quiz = '%s'" % (password, userid, username, quiz))
            db.commit()
            flash("비밀번호가 변경 되었습니다.")
            return redirect("/")
        else:
            flash("비밀번호를 변경할 수 없습니다.(정보 불일치)")
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
    flash("로그아웃 되었습니다.")
    return redirect('/')

#류재범 추가
@app.route("/game", methods=["GET", "POST"])
def game():
    return render_template("/game.html")

#류재범 추가
@app.route("/curriculum", methods=["GET", "POST"])
def curriculum():
    print("카드 목록 들어옴")
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM card WHERE 1")
    card_list = json.dumps(cursor.fetchall(), ensure_ascii=False)
    return render_template('curriculum.html', title = "curriculum", cl = card_list)

@app.route("/curriculum_add", methods=['GET', 'POST'])
def curriculum_add():
    card_type = request.form.get('card_type')
    card_level = request.form.get('card_level')
    card_name = request.form.get('card_name')
    card_front = request.form.get('card_front')
    card_back = request.form.get('card_back')
    card_text = request.form.get('card_text')
    
    if(card_type is None or (card_type != "1" and card_type != "2")):
        flash("타입 에러")
        return redirect('/curriculum')

    if(card_type == "1"):
        #유효성 검사
        if(card_level is None or card_level == ""):
            flash("적용 스테이지를 입력해 주세요")
            return redirect('/curriculum')
        elif(card_name is None or card_name == ""):
            flash("카드 이름을 입력해 주세요")
            return redirect('/curriculum')
        elif(card_front is None or card_front == ""):
            flash("카드 앞면 설명을 입력해 주세요")
            return redirect('/curriculum')
        elif(card_back is None or card_back == ""):
            flash("카드 뒷면 설명을 입력해 주세요")
            return redirect('/curriculum')
        elif(card_text is None or card_text == ""):
            flash("카드 추가 설명을 입력해 주세요")
            return redirect('/curriculum')
        
        #type 1 add
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("INSERT INTO card SET card_type = '%s', card_level = '%s', card_name = '%s', card_front = '%s', card_back = '%s', card_text = '%s', datetime = '%s'" % (card_type, card_level, card_name, card_front, card_back, card_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()

        flash("설명 카드가 추가되었습니다.")
        return redirect('/curriculum')

    elif(card_type == "2"):
        #type 2 add
        print("type2 들어옴")
    
    return redirect('/curriculum')

    """
    elif(card_level is None or card_level == ""):
        flash("적용 스테이지를 입력하세요.")
        return redirect('/curriculum')
    elif(card_level is None or card_level == ""):
    elif(card_level is None or card_level == ""):
    elif(card_level is None or card_level == ""):
    else:
        return redirect('/curriculum')
    """

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