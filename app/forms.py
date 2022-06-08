from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp


class SignUpForm(FlaskForm):
    username = StringField('아이디', validators=[DataRequired('아이디는 필수입력 항목입니다.'), Length(min=3, max=25, message='아이디는 3~25자 이내여야 합니다'), Regexp('^[A-Za-z][A-Za-z0-9]*$', message='아아디는 영문 및 숫자만 사용할 수 있습니다.')])
    nickname = StringField('닉네임', validators=[DataRequired('닉네임은 필수입력 항목입니다.'), Length(min=2, max=25, message='닉네임은 2~25자 이내여야 합니다')])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수입력 항목입니다.'), EqualTo('password_validate', '비밀번호가 일치하지 않습니다')])
    password_validate = PasswordField('비밀번호 확인', validators=[DataRequired('비밀번호 확인은 필수입력 항목입니다.')])
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력 항목입니다.'), Email()])
    profile_image = FileField('프로필 사진', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], '프로필 사진은 이미지 파일만 업로드할 수 있습니다.')])
    about_me = StringField('자기소개')


class LoginForm(FlaskForm):
    username = StringField('아이디', validators=[DataRequired('아이디는 필수입력 항목입니다.')])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수입력 항목입니다.')])
