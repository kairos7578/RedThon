from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class UserCreateForm(FlaskForm) :
    username = StringField('사용자이름', validators=[
        DataRequired(), Length(min=3, max=25)
    ])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')
    ])
