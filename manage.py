import os
from app import create_app, db
from app.models import Image


app = create_app(os.getenv('FLASK_ENV', 'production'))


def make_shell_context():
    return dict(db=db, Image=Image)

app.shell_context_processor(make_shell_context)


"""create table: image"""
@app.cli.command('create_table')
def create_table():
    db.create_all()


if __name__ == '__main__':
    app.run()
