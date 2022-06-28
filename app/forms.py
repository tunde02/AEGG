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


class MageForm(FlaskForm):
    name = StringField('균열 마법사 이름', validators=[DataRequired('균열 마법사 이름은 필수입력 항목입니다.')])
    name_en = StringField('균열 마법사 영어 이름', validators=[DataRequired('균열 마법사 영어 이름은 필수입력 항목입니다.')])
    series = StringField('균열 마법사 소속 시리즈', validators=[DataRequired('균열 마법사 소속 시리즈는 필수입력 항목입니다.')])
    series_en = StringField('균열 마법사 소속 시리즈 영어', validators=[DataRequired('균열 마법사 소속 시리즈 영어는 필수입력 항목입니다.')])
    ability_name = StringField('균열 마법사 능력 이름', validators=[DataRequired('균열 마법사 능력 이름은 필수입력 항목입니다.')])
    ability_name_en = StringField('균열 마법사 능력 영어 이름', validators=[DataRequired('균열 마법사 능력 영어 이름은 필수입력 항목입니다.')])
    ability = TextAreaField('균열 마법사 능력', validators=[DataRequired('균열 마법사 능력은 필수입력 항목입니다.')])
    ability_en = TextAreaField('균열 마법사 능력 영어', validators=[DataRequired('균열 마법사 능력 영어는 필수입력 항목입니다.')])
    activation_time = StringField('균열 마법사 능력 발동 시기', validators=[DataRequired('균열 마법사 능력 발동 시기는 필수입력 항목입니다.')])
    activation_time_en = StringField('균열 마법사 능력 발동 시기 영어', validators=[DataRequired('균열 마법사 능력 발동 시기 영어는 필수입력 항목입니다.')])
    required_charges = StringField('균열 마법사 능력 요구 충전수', validators=[DataRequired('균열 마법사 능력 요구 충전수는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='균열 마법사 능력 요구 충전수는 숫자만 입력할 수 습니다.')])
    image = FileField('균열 마법사 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '균열 마법사 이미지는 이미지 파일만 업로드할 수 있습니다.')])
    board_image = FileField('균열 마법사 보드 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '균열 마법사 보드 이미지는 이미지 파일만 업로드할 수 있습니다.')])
    back_board_image = FileField('균열 마법사 보드 뒷면 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '균열 마법사 보드 뒷면 이미지는 이미지 파일만 업로드할 수 있습니다.')])


class CardForm(FlaskForm):
    name = StringField('카드 이름', validators=[DataRequired('카드 이름은 필수입력 항목입니다.')])
    name_en = StringField('카드 영어 이름', validators=[DataRequired('카드 영어 이름은 필수입력 항목입니다.')])
    type = StringField('카드 타입', validators=[DataRequired('카드 타입은 필수입력 항목입니다.')])
    type_en = StringField('카드 영어 타입', validators=[DataRequired('카드 영어 타입은 필수입력 항목입니다.')])
    cost = StringField('카드 비용', validators=[DataRequired('카드 비용는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='카드 비용은 숫자만 입력할 수 있습니다.')])
    effect = TextAreaField('카드 효과', validators=[DataRequired('카드 효과는 필수입력 항목입니다.')])
    effect_en = TextAreaField('카드 영어 효과', validators=[DataRequired('카드 영어 효과는 필수입력 항목입니다.')])
    tier = StringField('카드 티어', validators=[DataRequired('카드 티어는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='카드 티어는 숫자만 입력할 수 있습니다.')])
    hp = StringField('카드 체력', validators=[DataRequired('카드 체력은 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='카드 체력은 숫자만 입력할 수 있습니다.')])
    image = FileField('카드 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '카드 이미지는 이미지 파일만 업로드할 수 있습니다.')])


class NemesisForm(FlaskForm):
    name = StringField('네메시스 이름', validators=[DataRequired('네메시스 이름은 필수입력 항목입니다.')])
    name_en = StringField('네메시스 이름 (English)', validators=[DataRequired('네메시스 이름 (English)은 필수입력 항목입니다.')])
    series = StringField('네메시스 소속 시리즈', validators=[DataRequired('네메시스 소속 시리즈는 필수입력 항목입니다.')])
    series_en = StringField('네메시스 소속 시리즈 (English)', validators=[DataRequired('네메시스 소속 시리즈 (English)는 필수입력 항목입니다.')])
    tier = StringField('네메시스 티어', validators=[DataRequired('네메시스 티어는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='네메시스 티어는 숫자만 입력할 수 있습니다.')])
    difficulty = StringField('네메시스 난이도', validators=[DataRequired('네메시스 난이도는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='네메시스 난이도는 숫자만 입력할 수 있습니다.')])
    hp = StringField('네메시스 체력', validators=[DataRequired('네메시스 체력는 필수입력 항목입니다.'), Regexp('^[0-9]*$', message='네메시스 체력은 숫자만 입력할 수 있습니다.')])
    setup = TextAreaField('네메시스 세팅', validators=[DataRequired('네메시스 세팅은 필수입력 항목입니다.')])
    setup_en = TextAreaField('네메시스 세팅 (English)', validators=[DataRequired('네메시스 세팅 (English)은 필수입력 항목입니다.')])
    additional_rules = TextAreaField('추가 규칙', validators=[DataRequired('추가 규칙은 필수입력 항목입니다.')])
    additional_rules_en = TextAreaField('추가 규칙 (English)', validators=[DataRequired('추가 규칙 (English)은 필수입력 항목입니다.')])
    unleash = TextAreaField('Unleash', validators=[DataRequired('Unleash는 필수입력 항목입니다.')])
    unleash_en = TextAreaField('Unleash (English)', validators=[DataRequired('Unleash (English)는 필수입력 항목입니다.')])
    increased_diff = TextAreaField('어려운 난이도 규칙', validators=[DataRequired('어려운 난이도 규칙은 필수입력 항목입니다.')])
    increased_diff_en = TextAreaField('어려운 난이도 규칙 (English)', validators=[DataRequired('어려운 난이도 규칙 (English)은 필수입력 항목입니다.')])
    image = FileField('네메시스 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '네메시스 이미지는 이미지 파일만 업로드할 수 있습니다.')])
    board_image = FileField('네메시스 보드 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '네메시스 보드 이미지는 이미지 파일만 업로드할 수 있습니다.')])
    back_board_image = FileField('네메시스 보드 뒷면 이미지', validators=[FileAllowed(['png', 'jpg', 'jpeg'], '네메시스 보드 뒷면 이미지는 이미지 파일만 업로드할 수 있습니다.')])


class ReviewForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('리뷰 내용은 필수입력 항목입니다.')])
    score = StringField('리뷰 점수', validators=[DataRequired('리뷰 점수는 필수입력 항목입니다.')])
