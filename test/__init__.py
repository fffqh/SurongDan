# from contextlib import redirect_stderr
import unittest
# import requests
import datetime
from flask import current_app,url_for,json,session
import sys
sys.path.append(".")

from surongdan import create_app, db
from api import users
from api import projects
from surongdan.extensions import db, mail_obj
from surongdan.settings import config
from surongdan.models import user_table ,project_table,dataset_table

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        u = user_table(user_name='admin',
                       user_email='admin@qq.com',
                       user_status=True,
                       user_is_admin=True)
        u.set_password('admin123')
        dateset =    dataset_table( dataset_id =  1,
                                    dataset_path ='/root/dataset')

        def_porj = project_table(
            # project_id = 1,
            project_user_id = 1,
            project_name = 'hahahah',
            project_info = 'heiheihei',
            project_dtime = datetime.datetime.now(),
            project_structure ='hdoashdousahd',
            # 输入输出
            project_dataset_id = 1,
            project_outpath = '/root',
            # 代码和状态
            project_code = 'print(hello) ',
            project_status = 'init',
            # 前端样式
            project_json = 'qianduanyangshi',
            # 缩略图
            project_image = 'suoluetu'
        )
        db.session.add(u)
        # db.session.commit()
        db.session.commit()
        
        db.session.add(dateset)
        db.session.commit()

        db.session.add(def_porj)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def add_with_session(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                sess['user_id'] =  1
                sess['user_name'] =  'admin'
                sess['user_email'] = 'admin@qq.com'
                sess['logged_in'] = True

    def test_home_page(self):
        response = self.client.get(url_for('users.index'))
        print(response)
        self.assertTrue(response.get_data(as_text=True))


    def test_login(self):
        data = {'email': "admin@qq.com",
                'user_info': 'admin',
                'user_pwd': 'admin123'
                }
        # headers = {"Content-Type": "application/x-www-form-urlencoded",
        #             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        #             "Referer": "http://www.renren.com/"}

        # url="localhost.localdomin:5000/users/index"

        response = self.client.post(url_for('users.login'),data=json.dumps(data),content_type='application/json')
        print(response)
        # print(r.cookies)
        self.add_with_session()
        # with open('test/session.txt','w') as f:
        #     f.write(response.cookies["session"])
        self.assertTrue(response.status_code == 200)

    def getSession(self):   # from file
        with open('test/session.txt','r') as f:
            return f.read()

    # def test_login(self):

    #     data={'user_info': 'admin','user_pwd': 'admin123'}
        
    #     data = json.dumps(data).encode()

    #     response = self.client.post(url_for('users.login'),
    #     data=data,content_type='application/json')
        
    #     print(response)
    #     self.assertTrue(response.status_code == 200)

    def test_logout(self):
        response = self.client.post(url_for('users.logout'))
        print(response)
        self.assertTrue(response.status_code == 202)
    # def test_savproj(self):


    def test_getproj(self):
        self.add_with_session()
        response = self.client.post(url_for('projects.getproj'),
        data=json.dumps({'proj_id':1}),content_type='application/json')
        print(response)
        self.assertTrue(response.status_code == 200)


if __name__ == '__main__':
    unittest.main()