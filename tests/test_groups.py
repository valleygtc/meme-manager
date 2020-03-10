import unittest
import json

from meme_manager import db, Image, Group

from tests import test_app


def fake_records(n):
    for i in range(1, n+1):
        group = Group(
            name=f'testGroup{i}',
        )
        img1 = Image(
            data=b'abcdefggggggg',
            img_type='jpeg',
            tags='aTag,bTag'
        )
        img2 = Image(
            data=b'abcdefggggggg',
            img_type='jpeg',
            tags='aTag,bTag'
        )
        group.images = [img1, img2]
        db.session.add(group)
    db.session.commit()


class TestGroupsShow(unittest.TestCase):
    url = '/api/groups/'

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(3)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_normal(self):
        client = test_app.test_client()
        resp = client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('data', json_data)


class TestGroupAdd(unittest.TestCase):
    url = '/api/groups/add'

    data = {
        'name': 'addedGroup'
    }

    def setUp(self):
        with test_app.app_context():
            db.create_all()
    
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
        # 验证已插入数据库
        with test_app.app_context():
            self.assertTrue(Group.query.get(1))


class TestGroupDelete(unittest.TestCase):
    url = '/api/groups/delete'

    def setUp(self):
        with test_app.app_context():
            db.create_all()
            fake_records(1)
    
    def tearDown(self):
        with test_app.app_context():
            db.drop_all()

    def test_normal(self):
        client = test_app.test_client()
        resp = client.post(
            self.url,
            json={'name': 'testGroup1'}
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertIn('msg', json_data)
        # 验证数据库中已删除
        with test_app.app_context():
            self.assertFalse(Group.query.filter_by(name='testGroup1').first())
            # 验证 cascade delete：
            self.assertFalse(Image.query.get(1))
            self.assertFalse(Image.query.get(2))
    
    def test_delete_not_exists_group(self):
        client = test_app.test_client()
        resp = client.post(
            self.url,
            json={'name': 'not_exists_group'}
        )
        self.assertEqual(resp.status_code, 404)
        json_data = resp.get_json()
        self.assertIn('error', json_data)


class TestGroupUpdate(unittest.TestCase):
    url = '/api/groups/update'

    data = {
        'name': 'testGroup1',
        'new_name': 'updatedGroup',
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
        # 验证数据库中确实已经更新
        with test_app.app_context():
            record = Group.query.get(1)
            self.assertEqual(record.name, self.data['new_name'])
