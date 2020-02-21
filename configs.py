import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

    @classmethod
    def init_app(cls, app):
        return app


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        app.logger.setLevel(logging.INFO)
        # 注：Flask默认StreamHandler：所有级别 -> wsgi_errors_stream(which is usually sys.stderr)

        # WARNING -> log file
        if not os.path.isdir('log'):
            os.mkdir('log')

        fh = TimedRotatingFileHandler(
            'log/warning.log',
            when='midnight',
            interval=1,
            backupCount=3,
            encoding='utf-8',
        )
        fh.setLevel(logging.WARNING)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        fh.setFormatter(formatter)
        app.logger.addHandler(fh)

        return app


configs = {
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'production': ProductionConfig,
}
