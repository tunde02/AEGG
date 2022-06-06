from config.default import *
from logging.config import dictConfig


SQLALCHEMY_DATABASE_URI =  'mysql://root:PASSWORD@127.0.0.1:3306/DATABASE_NAME'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'product'

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
UPLOAD_FOLDER = './app/static/images'

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/aegg.log'),
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})
