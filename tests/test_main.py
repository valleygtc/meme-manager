import unittest
import sys
import json
from io import BytesIO

from app import db
from app.models import Image

from tests import test_app


def fake_records(n):
    for i in range(n):
        img = Image(
            data=b'abcdefggggggg',
            img_type='jpeg',
            tags='aTag,bTag'
        )
        db.session.add(img)
    db.session.commit()


class TestImageShow(unittest.TestCase):
    url = '/images/'

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(20)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_show_all_images(self):
        client = test_app.test_client()
        resp = client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)
    
    def test_show_one_images_data(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={'id': 1}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'image/jpeg')
        self.assertEqual(resp.headers.get('Content-Type'), 'image/jpeg')
    
    def test_pagination(self):
        client = test_app.test_client()
        resp = client.get(self.url, query_string={
            'page': 2,
            'per_page': 10,
        })
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)
        self.assertIn('pagination', json_data)
        self.assertEqual(len(json_data['data']), 10)


class TestImageAdd(unittest.TestCase):
    url = '/images/add'

    data = {
        'image': (BytesIO(b'added image data'), 'test_image.jpeg'),
        'metadata': json.dumps({
            'img_type': 'jpeg',
            'tags': ['aTag', 'bTag']
        })
    }

    def setUp(self):
        with test_app.app_context():
            db.create_all()
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_default(self):
        client = test_app.test_client()
        body = self.data.copy()
        resp = client.post(
            self.url,
            data=body
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('msg', json_data)
        # 验证已插入数据库
        with test_app.app_context():
            self.assertTrue(Image.query.get(1))


class TestImageDelete(unittest.TestCase):
    url = '/images/delete'

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(1)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_normal(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={'id': 1}
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('msg', json_data)
        # 验证数据库中已删除
        with test_app.app_context():
            self.assertFalse(Image.query.get(1))
    
    def test_delete_not_exists_image(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={'id': 10000}
        )
        self.assertEqual(resp.status_code, 404)
        json_data = resp.get_json()
        self.assertIn('error', json_data)


class TestTagsShow(unittest.TestCase):
    url = '/tags/'

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
    url = '/tags/add'

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
    url = '/tags/delete'

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


if __name__ == '__main__':
    if sys.argv[1] == 'fake_records':
        fake_records(20)
