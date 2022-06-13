from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from pymysql import install_as_MySQLdb


install_as_MySQLdb()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from app import models

    # Blueprints
    from app.views import main_views, auth_views, profile_views, post_views, comment_views, wiki_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(profile_views.bp)
    app.register_blueprint(post_views.bp)
    app.register_blueprint(comment_views.bp)
    app.register_blueprint(wiki_views.bp)

    # Filters
    from app.filter import datetime_format, datetime_detail_format
    app.jinja_env.filters['datetime'] = datetime_format
    app.jinja_env.filters['datetime_detail'] = datetime_detail_format

    # Markdown
    Markdown(app, extensions=['nl2br', 'fenced_code'])

    return app
