import os
from pathlib import Path

import click
from waitress import serve

from .create_app import create_app
from .models import db, Image


@click.group()
def cli():
    """meme-manager cli."""


@cli.command('init_db')
@click.argument('db_file', default='memes.sqlite')
def init_db(db_file):
    """Initialize sqlite database file."""
    fp = Path(db_file).resolve().absolute()
    if fp.exists():
        print(f'Error: {fp} has already exists.')
        return

    app = create_app(os.getenv('FLASK_ENV', 'production'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{fp}'
    with app.app_context():
        db.create_all()
        print(f'Initialize {fp} done.')


@cli.command('run')
@click.option('--port', default=5000, help='Network port to listen to.')
@click.argument('db_file', default='memes.sqlite')
def run(port, db_file):
    """Run meme-manager server."""
    fp = Path(db_file).resolve().absolute()
    if not fp.exists():
        print(f'Error: {fp} not exists.')
        return

    app = create_app(os.getenv('FLASK_ENV', 'production'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{fp}'
    serve(app, host='127.0.0.1', port=port)


def file2record(file):
    """
    Params:
        file [Path]
    Return:
        record [Image]
    """
    return Image(
        data=file.read_bytes(),
        img_type=file.suffix[1:],
        tags=file.stem,
    )


def import_from_dir(src_path):
    """
    Params:
        src_path [Path]
    Return:
        count [int]
    """
    count = 0
    for file in src_path.iterdir():
        if file.is_file():
            count += 1
            record = file2record(file)
            db.session.add(record)
    db.session.commit()
    return count


@cli.command('import')
@click.argument('src')
@click.argument('db_file')
def import_(src, db_file):
    """Import image file or directory"""
    src_path = Path(src)
    db_path = Path(db_file).resolve().absolute()
    if not src_path.exists():
        print(f'Error: {src_path} not exists.')
        return
    if not db_path.exists():
        print(f'Error: {db_path} not exists.')
        return

    app = create_app(os.getenv('FLASK_ENV', 'production'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    if src_path.is_file():
        with app.app_context():
            record = file2record(src_path)
            db.session.add(record)
            db.session.commit()
            print(f'Add image {src_path} done.')
    elif src_path.is_dir():
        with app.app_context():
            count = import_from_dir(src_path)
            print(f'Add {count} images done.')
    else:
        print(f'Error: {src_path} is not a regular file nor a directory.')
        return
