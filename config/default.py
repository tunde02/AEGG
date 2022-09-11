import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ALLOWED_EXTENSIONS = set(["tif", "pjp", "xbm", "svgz", "jpg", "jpeg", "ico", "tiff", "gif", "svg", "jfif", "webp", "png", "bmp", "pjpeg", "avif"])
UPLOAD_FOLDER = './app/static/images'
