import os
import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def show_entries_test(self):
        test = self.app.get("/")
        assert b'no entries there yet'in test.data

    def test_add_entry(self):
        self.app.post('/add', data=dict(
            title='Test Post',
            text='Hello world',
            categories='General'
        ), follow_redirects=True)
        test = self.app.get('/')
        self.assertIn(b'Test Add', test.data)

    def test_edit_entry(self):
        self.app.post('/add', data=dict(
            title='Old Title',
            text='Old text',
            categories='General'
        ))
        test = self.app.post('/edit/1', data=dict(
            title='New Title',
            text='Updated text',
            category='General'
        ), follow_redirects=True)
        self.assertIn(b'Edit', test.data)

    def test_delete_entry(self):
        self.app.post('/add', data=dict(
            title='Delete Me',
            text='Bye',
            categories='General'
        ))
        test = self.app.post('/delete/1', follow_redirects=True)
        self.assertNotIn(b'Delete', test.data)






if __name__ == '__main__':
    unittest.main()