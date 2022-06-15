from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, EmailField, TextAreaField
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


class PostForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired('제목은 필수입력 항목입니다.')])
    content = TextAreaField('내용')
    category = StringField('카테고리', validators=[DataRequired('카테고리는 필수입력 항목입니다.')])


class CommentForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('댓글 내용은 필수입력 항목입니다.')])


class CardForm(FlaskForm):
    name = StringField('카드 이름', validators=[DataRequired('카드 이름은 필수입력 항목입니다.')])
    name_en = StringField('카드 영어 이름', validators=[DataRequired('카드 영어 이름은 필수입력 항목입니다.')])
    type = StringField('카드 타입', validators=[DataRequired('카드 타입은 필수입력 항목입니다.')])
    type_en = StringField('카드 영어 타입', validators=[DataRequired('카드 영어 타입은 필수입력 항목입니다.')])
    cost = StringField('카드 비용', validators=[DataRequired('카드 비용는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='카드 비용은 숫자만 입력할 수 있습니다.')])
    effect = TextAreaField('카드 효과', validators=[DataRequired('카드 효과는 필수입력 항목입니다.')])
    effect_en = TextAreaField('카드 영어 효과', validators=[DataRequired('카드 영어 효과는 필수입력 항목입니다.')])
    image = FileField('카드 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '카드 이미지는 이미지 파일만 업로드할 수 있습니다.')])
