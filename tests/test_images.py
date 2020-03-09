import unittest
import json
from io import BytesIO

from meme_manager import db, Image, Group

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
    url = '/api/images/'

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


class TestImageSearch(unittest.TestCase):
    url = '/api/images/'

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            group = Group(
                name=f'testGroup',
            )
            img1 = Image(
                data=b'abcdefggggggg',
                img_type='jpeg',
                tags='aTag',
            )
            img2 = Image(
                data=b'abcdefggggggg',
                img_type='jpeg',
                tags='bTag',
            )
            group.images = [img1, img2]
            db.session.add(group)
            img3 = Image(
                data=b'abcdefggggggg',
                img_type='jpeg',
                tags='cTag',
            )
            db.session.add(img3)
            db.session.commit()
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()
    
    def test_search_tag(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={'tag': 'aTag'}
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)
        self.assertEqual(len(json_data['data']), 1)

    def test_search_group(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={'group': 'testGroup'}
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)
        self.assertEqual(len(json_data['data']), 2)
    
    def test_search_tag_within_group(self):
        client = test_app.test_client()
        resp = client.get(
            self.url,
            query_string={
                'group': 'testGroup',
                'tag': 'aTag',
            }
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)
        self.assertEqual(len(json_data['data']), 1)


class TestImageAdd(unittest.TestCase):
    url = '/api/images/add'

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
    url = '/api/images/delete'

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
