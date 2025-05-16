import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev"
    TESTING = True
    WTF_CSRF_ENABLED = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@db:5432/twitterdb"
    DEBUG = True
