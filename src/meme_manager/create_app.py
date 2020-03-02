from flask import Flask

from .configs import configs


def create_app(config_name='production'):
    app = Flask(
        __name__,
        static_folder='frontend',
        static_url_path='',
    )
    config = configs[config_name]
    app.config.from_object(config)
    config.init_app(app)

    from .views import bp_main
    app.register_blueprint(bp_main)

    from .models import db, Image
    db.init_app(app)

    def make_shell_context():
        return dict(db=db, Image=Image)

    app.shell_context_processor(make_shell_context)

    return app
