import datetime
import pickle
from flask import current_app
from flask import request, jsonify, Blueprint, session
from flask import send_file
from sqlalchemy import and_

from surongdan.models import project_table, layer_table, dataset_table
from surongdan.precode import *
from surongdan.gencode import *


run_bp = Blueprint('run', __name__)

@run_bp.route('/test_gen_code', methods={'GET'})
def test_gen_code():
    if gen_code(3):
        return jsonify({'msg':'ok'}), 201
    else:
        return jsonify({'fault':'false'}), 500

# 获取数据集
@run_bp.route('/get_dataset_list', methods={'GET'})
def get_dataset_list():
    # 用户是否登录的检查
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'fault': 'please login!'}), 403
    # 查询所有可以使用的数据集
    dataset_objs = dataset_table.query.all()
    dataset_lst = []
    for dataset in dataset_objs:
        dataset_lst.append({'dataset_id':dataset.dataset_id, 
                            'dataset_name':dataset.dataset_name, 
                            'dataset_desc':dataset.dataset_desc})
    return jsonify(dataset_lst), 200

# 获取代码
@run_bp.route('/get_code/<project_id>', methods={'GET'})
def get_code(project_id):
    # 用户是否登录的检查
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'fault': 'please login!'}), 403
    # 查询项目
    p = project_table.query.get(int(project_id))
    if p is None:
        return jsonify({'fault':'project does not exist'}), 404
    # 代码已生成，直接返回
    if p.project_status == 'done':
        return jsonify({'msg':'ok', 
                        'project_code': p.project_code, 
                        'environment': 'Pytorch',
                        'path':'/run/urlforcode/'+project_id})
    # 需要生成代码
    if p.project_status == 'init':
        # 生成代码
        gen_code(p.project_id)
        # 将代码存入数据库
        with open(p.project_outpath+'/code.py', 'r') as f:
            content = f.read()
            p.project_code = content
        p.project_status = 'done'
        return jsonify({'msg':'ok', 
                        'project_code': p.project_code, 
                        'environment': 'Pytorch', 
                        'path':'/run/urlforcode/'+project_id})

# 获取代码的静态资源文件
@run_bp.route('/urlforcode/<project_id>', methods={'GET'})
def urlforcode(project_id):
    # 检查用户是否登录
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'fault': 'please login!'}), 403
    # 
    p = project_table.get(int(project_id))
    if p is None:
        return jsonify({'fault':'project does not exist'}), 404
    return send_file(p.project_outpath+'/'+project_id+'/code.py'), 200


