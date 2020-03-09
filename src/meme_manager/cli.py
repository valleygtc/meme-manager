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


def image2filename(image):
    """
    Params:
        image [Image]:
    Return:
        filename [str]
    """
    filename = image.tags.split(',')[0] or str(uuid.uuid4())
    filename += f'.{image.img_type}'
    return filename


def assert_safe_filepath(filepath):
    """if filepath exists, generate a uuid filename replact it.
    Params:
        filepath [Path]
    Return:
        filepath [Path]
    """
    if filepath.exists():
        return filepath.with_name(str(uuid.uuid4()) + filepath.suffix)
    else:
        return filepath


def export_group(dest_dir, group):
    """
    Params:
        dest_dir [Path]:
        group [str]:
    Return:
        ok_count, fail_count
    """
    grecord = Group.query.filter_by(name=group).first()
    if not grecord:
        print(f'Error: group {group} not exists.')
        return

    group_dir = dest_dir/group
    if group_dir.exists():
        print(f'Error: {group_dir} already exists.')
        return

    try:
        group_dir.mkdir()
    except OSError as e:
        print(f'Error: {e}')
        return

    ok_count = 0
    fail_count = 0
    for image in grecord.images:
        filename = image2filename(image)
        filepath = group_dir/filename
        filepath = assert_safe_filepath(filepath)
        try:
            with open(filepath, 'wb') as fh:
                fh.write(image.data)
        except OSError:
            print(f'Error: {filepath} write failed.')
            fail_count += 1
        else:
            print(f'export {filepath} done.')
            ok_count +=1
    return ok_count, fail_count


def export_all(dest_dir):
    """
    Params:
        dest_dir [Path]:
    Return:
        ok_count, fail_count
    """
    # groups
    for group in Group.query.all():
        group_dir = dest_dir/group.name
        if group_dir.exists():
            print(f'Error: {group_dir} already exists.')
            return

        try:
            group_dir.mkdir()
        except OSError as e:
            print(f'Error: {e}')

    # images
    ok_count = 0
    fail_count = 0
    for image in Image.query.all():
        filename = image2filename(image)
        filepath = dest_dir/image.group.name/filename if image.group else dest_dir/filename
        filepath = assert_safe_filepath(filepath)
        try:
            with open(filepath, 'wb') as fh:
                fh.write(image.data)
        except OSError:
            print(f'Error: {filepath} write failed.')
            fail_count += 1
        else:
            print(f'export {filepath} done.')
            ok_count +=1
    return ok_count, fail_count


@cli.command('export')
@click.option('-g', '--group', help='Specify group.')
@click.argument('db_file')
@click.argument('dest')
def export_(group, db_file, dest):
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
    with app.app_context():
        if group:
            # export -g <dir>
            ok_count, fail_count = export_group(dest_path, group)
        else:
            # export <dir>
            ok_count, fail_count = export_all(dest_path)

    print(f'Total export {ok_count + fail_count} images.')
    print(f'Success: {ok_count}')
    print(f'Failed: {fail_count}')
