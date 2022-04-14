from flask import request, jsonify, session, make_response 

from surongdan import app, db
from surongdan.models import user_table 

import re

############ 设置路由 ###########
# 首页，欢迎
@app.route('/')
def index():
    name = request.cookies.get('name', 'Human')
    response = '<h1>Hello %s</h1>' % name
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response

# 负责处理注册请求
@app.route('/users/register', methods={'POST'})
def register():
    data = request.get_json()
    #print(data)    
    #print(data['user_name'])
    # 判断name是否重复
    if(user_table.query.filter_by(user_name = data['user_name']).first()):
        return jsonify({'fault':'user_name is invalid!'}), 202
    # 判断email是否重复
    if(user_table.query.filter_by(user_email = data['user_email']).first()):
        return jsonify({'fault':'user_email is invalid!'}), 202
    u = user_table( user_name = data['user_name'],
                    user_email = data['user_email'],
                    user_pwd = data['user_pwd'],
                    user_status = True)
    db.session.add(u)
    db.session.commit()
    if(u.user_id == None):
        return jsonify({'fault':'something wrong'}), 202 
    else:
        return jsonify({'user_id':u.user_id, 'user_name':u.user_name}), 201

# 负责处理登录请求
@app.route('/users/login', methods={'POST'})
def login():
    # 查询用户当前是否重复登录
    name = request.cookies.get('name')
    print(name)
    if name and session.get('logged_in'):
        return jsonify({'fault':'You have already logged in'}), 202
    
    email_str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    data = request.get_json()
    u = None
    if re.match(email_str, data['user_info']):
        u = user_table.query.filter_by(user_email = data['user_info']).first()
    else:
        u = user_table.query.filter_by(user_name = data['user_info']).first()
    # 用户信息检查
    if(u == None):
        return jsonify({'fault':'user info error!'}), 203
    if(u.user_pwd != data['user_pwd']):
        return jsonify({'fault':'user info error!'}), 203
    if(u.user_status == False):
        return jsonify({'fault':'user is invalid!'}), 204

    # 登录成功
    session['logged_in'] = True
    response = make_response(jsonify({'user_id':u.user_id, 'user_name':u.user_name}))
    response.set_cookie('name', u.user_name)
    return response, 200

# 负责处理登出请求
@app.route('/users/logout', methods={'POST'})
def logout():
    # 删除session和cookie
    if(not session.get('logged_in')):
        response = jsonify({'info':'invalid logout'})
        response.delete_cookie('name')
        return response, 202
    session.pop('logged_in')
    response = jsonify({'info':'successful logout'})
    response.delete_cookie('name')
    return response, 200

