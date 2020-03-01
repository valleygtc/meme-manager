from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
from flask.cli import FlaskGroup

from .configs import configs


db = SQLAlchemy()


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

    db.init_app(app)

    def make_shell_context():
        return dict(db=db, Image=Image)

    app.shell_context_processor(make_shell_context)
    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the Wiki application."""


@cli.command('create_table')
def create_table():
    current_app.config['SQLALCHEMY_ECHO'] = True
    print(current_app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()


@cli.command('import_images_from_dir')
@click.argument('path')
def import_images_from_dir(path):
    count = 0
    p = Path(path)
    if not p.is_dir():
        raise Exception(f'{path} is not a directory.')
    
    for img in p.iterdir():
        if img.is_file():
            count += 1
            img_data = img.read_bytes()
            img_type = img.suffix[1:]
            tags = img.stem
            record = Image(
                data=img_data,
                img_type=img_type,
                tags=tags,
            )
            db.session.add(record)
    db.session.commit()
    print(f'总共导入 {count} 个图片。')
