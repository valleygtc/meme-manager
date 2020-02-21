from pathlib import Path

from app import db
from app.models import Image


def import_from_dir(path):
    count = 0
    p = Path(path)
    if not p.is_dir():
        raise Exception(f'{path} is not a directory.')
    
    for img in p.iterdir():
        if img.is_file():
            count += 1
            img_data = img.read_bytes()
            img_type = img.suffix
            tags = img.stem
            record = Image(
                data=img_data,
                img_type=img_type,
                tags=tags,
            )
            db.session.add(record)
    db.session.commit()
    return count
