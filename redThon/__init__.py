from flask import Flask, redirect, render_template, request

from redThon.pybo.forms import UserCreateForm

app = Flask(__name__)

@app.route("/")
def root():
    return render_template('index.html', title = "main")

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