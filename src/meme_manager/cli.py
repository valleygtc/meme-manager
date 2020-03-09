import os
from pathlib import Path
import webbrowser
import uuid

import click
from waitress import serve

from .version import __version__
from .create_app import create_app
from .models import db, Image, Group


@click.group()
@click.version_option(__version__)
def cli():
    """meme-manager cli."""


@cli.command('initdb')
@click.argument('db_file', default='memes.sqlite')
def initdb(db_file):
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
    webbrowser.open(f'http://127.0.0.1:{port}/index.html')
    serve(app, host='127.0.0.1', port=port)


def file2image(file, group_id=None):
    """
    Params:
        file [Path]
    Return:
        image [Image]
    """
    if not file.is_file():
        raise Exception(f'file2image parameter {file} must be a regular file.')

    return Image(
        data=file.read_bytes(),
        img_type=file.suffix[1:],
        tags=file.stem,
        group_id=group_id,
    )


def assert_group(name):
    """
    Params:
        name [str]
    Return:
        group_id [int]
    """
    record = Group.query.filter_by(name=name).first()
    if record:
        return record.id
    else:
        group = Group(name=name)
        db.session.add(group)
        db.session.flush()
        return group.id


def import_flat_dir(dir_, group):
    """
    Params:
        dir_ [Path]
        group [str]
    Return:
        count [int]: images num.
    """
    print(f'Group: {group}')
    count = 0
    group_id = assert_group(group)
    
    for f in dir_.iterdir():
        if f.is_file():
            image = file2image(f, group_id)
            db.session.add(image)
            count += 1
            print(f'Add image {f} done.')
    db.session.commit()
    return count


def import_struct_dir(dir_):
    """
    Params:
        dir_ [Path]
        group [str]
    Return:
        group_count [int], file_count [int]
    """
    gcount = 0
    fcount = 0
    for p in dir_.iterdir():
        if p.is_file():
            image = file2image(p)
            db.session.add(image)
            fcount += 1
            print(f'Add image {p} done.')
        elif p.is_dir():
            fc = import_flat_dir(p, p.name)
            gcount += 1
            fcount += fc
    db.session.commit()
    return gcount, fcount


@cli.command('import')
@click.option('-g', '--group', help='Set group.')
@click.argument('src')
@click.argument('db_file')
def import_(group, src, db_file):
    """Import image file or directory."""
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
            # import <file>
            # import -g <file>
            group_id = assert_group(group) if group else None
            image = file2image(src_path, group_id)
            db.session.add(image)
            db.session.commit()
            print(f'Add image {src_path} done.')
    elif src_path.is_dir():
        with app.app_context():
            if group:
                # import -g <dir>: import dir only contain files.
                fcount = import_flat_dir(src_path, group)
                print(f'Total add {fcount} images.')
            else:
                # import <dir>: import dir contain files and dirs.
                gcount, fcount = import_struct_dir(src_path)
                print(f'Total add {gcount} group, {fcount} images.')
    else:
        print(f'Error: {src_path} is not a regular file nor a directory.')
        return


@cli.command('export')
@click.argument('db_file')
@click.argument('dest')
def export_(db_file, dest):
    """Export db images to a directory."""
    db_path = Path(db_file).resolve().absolute()
    dest_path = Path(dest)
    if not db_path.exists():
        print(f'Error: {db_path} not exists.')
        return
    if not dest_path.exists():
        print(f'Error: {dest_path} not exists.')
        return
    if not dest_path.is_dir():
        print(f'Error: {dest_path} is not a directory.')
        return

    app = create_app(os.getenv('FLASK_ENV', 'production'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    ok_count = 0
    fail_count = 0
    with app.app_context():
        # groups
        for group in Group.query.all():
            dir_ = dest_path/group.name
            if dir_.exists():
                print(f'Error: {dir_} already exists.')
                return

            try:
                dir_.mkdir()
            except OSError as e:
                print(f'Error: {e}')

        # images
        for image in Image.query.all():
            filename = image.tags.split(',')[0] or str(uuid.uuid4())
            filename += f'.{image.img_type}'
            filepath = dest_path/image.group.name/filename if image.group else dest_path/filename
            try:
                with open(filepath, 'wb') as fh:
                    fh.write(image.data)
            except OSError:
                print(f'Error: {filename} write failed.')
                fail_count += 1
            else:
                print(f'export {filename} done.')
                ok_count +=1
    print(f'Total export {ok_count + fail_count} images.')
    print(f'Success: {ok_count}')
    print(f'Failed: {fail_count}')
