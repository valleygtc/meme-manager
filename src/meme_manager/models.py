from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    create_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())

    def __repr__(self):
        return '<Group %r>' % self.id


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary(length=2**24-1), nullable=False) # max size: 16MB
    img_type = db.Column(db.String(64), nullable=False)
    tags = db.Column(db.Text(), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey(Group.id))
    group = db.relationship(Group, backref=db.backref('images', lazy=True, cascade="all,delete"))
    create_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())

    def readyToJSON(self, keys, datetime_format):
        """
        Params:
            keys [Iterable[str]]
            datetime_format [str]: 同datetime.strptime()的格式声明
        """
        d = {}
        for k in keys:
            if k == 'create_at':
                v = getattr(self, k).strftime(datetime_format)
            elif k == 'tags':
                v = getattr(self, k).split(',')
            elif k == 'group':
                v = self.group.name if self.group else None
            else:
                v = getattr(self, k)
            d[k] = v
        return d

    def __repr__(self):
        return '<Image %r>' % self.id
