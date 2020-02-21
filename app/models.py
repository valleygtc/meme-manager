from sqlalchemy.sql import func

from . import db


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary(), nullable=False)
    img_type = db.Column(db.String(64), nullable=False)
    tags = db.Column(db.Text(), nullable=False)
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
            else:
                v = getattr(self, k)
            d[k] = v
        return d

    def __repr__(self):
        return '<Image %r>' % self.id
