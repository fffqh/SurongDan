import datetime
import random
import re

from flask import request, jsonify, session, make_response, Blueprint

from surongdan.extensions import db
from surongdan.mail import *
from surongdan.models import user_table

users_bp = Blueprint('users', __name__)

# 存放用户对应的验证码
mails_verified_list = {}


############ 设置路由 ###########
# 首页，欢迎
@users_bp.route('/')
def index():
    name = request.cookies.get('name', 'Human')
    response = '<h1>Hello %s</h1>' % name
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response

@users_bp.route('/get_verified', methods={'POST'})
def verified():
    data = request.get_json()
    print(data)
    code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for _ in range(6))
    user_email = data['user_email']
    send_mail(user_email, '验证码', '您的验证码为' + code)
    # 记录验证码信息，前一个为验证码，后一个为验证码发出时的时间
    mails_verified_list[user_email] = (code, datetime.datetime.now())
    return jsonify({'info':'ok'}), 200

# 负责处理注册请求
@users_bp.route('/register', methods={'POST'})
def register():
    data = request.get_json()
    print(data)
    # print(data['user_name'])
    # 判断name是否重复
    if user_table.query.filter_by(user_name=data['user_name']).first():
        return jsonify({'fault': 'user_name is invalid!'}), 401
    # 判断email是否重复
    if user_table.query.filter_by(user_email=data['user_email']).first():
        return jsonify({'fault': 'user_email is invalid!'}), 401
    # 判断验证码是否正确
    if data['user_email'] not in mails_verified_list.keys() or data['user_verify'] != \
            mails_verified_list[data['user_email']][0]:
        return jsonify({'fault': 'user_verify is invalid!'}), 403
    # 判断验证码是否超时，超过十分钟则失效
    min = (datetime.datetime.now() - mails_verified_list[data['user_email']][1]).seconds / 60
    if min > 10:
        return jsonify({'fault': 'user_verify is overdue!'}), 403

    u = user_table(user_name=data['user_name'],
                   user_email=data['user_email'],
                   # user_pwd=data['user_pwd'],
                   user_status=True)
    u.set_password(data['user_pwd'])
    db.session.add(u)
    db.session.commit()
    if (u.user_id == None):
        return jsonify({'fault': 'something wrong'}), 500
    else:
        return jsonify({'user_id': u.user_id, 'user_name': u.user_name}), 201


# 找回密码
@users_bp.route('/findback', methods={'POST'})
def find_back():
    data = request.get_json()
    # 判断email是否存在
    u = user_table.query.filter_by(user_email=data['user_email']).first()
    if u is None:
        return jsonify({'fault': 'user_email is invalid!'}), 202
    # 判断验证码是否正确
    if data['user_email'] not in mails_verified_list.keys() or data['user_verify'] != \
            mails_verified_list[data['user_email']][0]:
        return jsonify({'fault': 'user_verify is invalid!'}), 202
    # 判断验证码是否超时，超过十分钟则失效
    min = (datetime.datetime.now() - mails_verified_list[data['user_email']][1]).seconds / 60
    if min > 10:
        return jsonify({'fault': 'user_verify is overdue!'}), 202

    u.user_pwd = data['user_pwd']

    db.session.commit()
    if u.user_id == None:
        return jsonify({'fault': 'something wrong'}), 202
    else:
        return jsonify({'user_id': u.user_id, 'user_name': u.user_name}), 201


# 负责处理登录请求
@users_bp.route('/login', methods={'POST'})
def login():
    # 查询用户当前是否重复登录
    name = request.cookies.get('name')
    print(name)
    if name and session.get('logged_in'):
        return jsonify({'fault': 'You have already logged in'}), 204
    email_str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    data = request.get_json()
    print(data)
    u = None
    if re.match(email_str, data['user_info']):
        u = user_table.query.filter_by(user_email=data['user_info']).first()
    else:
        u = user_table.query.filter_by(user_name=data['user_info']).first()
    # 用户信息检查
    if (u == None):
        return jsonify({'fault': 'user info error!'}), 401
    if (u.validate_password(data['user_pwd']) == False):
        return jsonify({'fault': 'user info error!'}), 401
    # if (u.user_pwd != data['user_pwd']):
    #     return jsonify({'fault': 'user info error!'}), 401
    if (u.user_status == False):
        return jsonify({'fault': 'user is invalid!'}), 403

    # 登录成功
    # 登陆成功，在全局变量中储存用户信息
    session['logged_in'] = True
    session['user_id'] = u.user_id
    session['user_name'] = u.user_name
    session['user_email'] = u.user_email
    session['user_is_admin'] = u.user_is_admin
    response = make_response(jsonify({'user_id': u.user_id, 'user_name': u.user_name}))
    response.set_cookie('name', u.user_name)
    return response, 200


# 负责处理登出请求
@users_bp.route('/logout', methods={'POST'})
def logout():
    # 删除session和cookie
    if (not session.get('logged_in')):
        response = jsonify({'info': 'invalid logout'})
        response.delete_cookie('name')
        return response, 202
    session.pop('logged_in')
    session.pop('user_id')
    session.pop('user_is_admin')
    session.pop('user_email')
    response = jsonify({'info': 'successful logout'})
    response.delete_cookie('name')
    return response, 200
