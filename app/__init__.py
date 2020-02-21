from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from configs import configs


db = SQLAlchemy()


def create_app(config_name='production'):
    app = Flask(__name__)
    config = configs[config_name]
    app.config.from_object(config)
    config.init_app(app)

    from .views import bp_main
    app.register_blueprint(bp_main)

    db.init_app(app)
    return app
