from config.default import *


SQLALCHEMY_DATABASE_URI = 'mysql://root:PASSWORD@127.0.0.1:3306/DATABASE_NAME'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev"

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
UPLOAD_FOLDER = './app/static/images'
