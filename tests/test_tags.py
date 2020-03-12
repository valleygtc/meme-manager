import unittest
import json
from io import BytesIO

from meme_manager import db, Image

from tests import test_app


def fake_records(n):
    for i in range(n):
        img = Image(
            data=b'abcdefggggggg',
            img_type='jpeg',
            tags=['aTag', 'bTag'],
        )
        db.session.add(img)
    db.session.commit()


class TestTagsShow(unittest.TestCase):
    url = '/api/tags/'

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(20)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_default(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={'image_id': 1}
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)


class TestTagsAdd(unittest.TestCase):
    url = '/api/tags/add'

    data = {
        'image_id': 1,
        'tags': ['addedTag1', 'addedTag2']
    }

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(1)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_default(self):
        client = test_app.test_client()
        body = self.data.copy()
        resp = client.post(self.url, json=body)
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('msg', json_data)
        # 验证已插入数据库
        with test_app.app_context():
            image = Image.query.get(1)
            self.assertIn('addedTag1', image.tags)
            self.assertIn('addedTag2', image.tags)


class TestTagDelete(unittest.TestCase):
    url = '/api/tags/delete'

    data = {
        'image_id': 1,
        'tag': 'aTag'
    }

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(1)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_normal(self):
        client = test_app.test_client()
        body = self.data.copy()
        resp = client.post(
            self.url,
            json=body
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('msg', json_data)
        # 验证数据库中已删除
        with test_app.app_context():
            image = Image.query.get(1)
            self.assertNotIn('aTag', image.tags)
