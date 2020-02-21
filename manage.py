import os

from flask import current_app
import click

from app import create_app, db
from app.models import Image
from utils.import_images import import_from_dir


app = create_app(os.getenv('FLASK_ENV', 'production'))


def make_shell_context():
    return dict(db=db, Image=Image)

app.shell_context_processor(make_shell_context)


"""create table: image"""
@app.cli.command('create_table')
def create_table():
    current_app.config['SQLALCHEMY_ECHO'] = True
    print(current_app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()


@app.cli.command('import_images_from_dir')
@click.argument('path')
def import_images_from_dir(path):
    num = import_from_dir(path)
    print(f'总共导入 {num} 个图片。')


if __name__ == '__main__':
    app.run()
