import datetime
import pickle

from flask import current_app
from flask import request, jsonify, Blueprint

from surongdan.extensions import db
from surongdan.models import project_table, layer_table

projects_bp = Blueprint('projects', __name__)


# 保存工程接口：projects/save_projinfo
@projects_bp.route('/save_projinfo', methods={'POST'})
def save_projinfo():
    config = current_app.config
    data = request.get_json()
    print(data)
    # 用户是否登录的检查 ## 待完成
    # 数据库处理
    if data['project_is_new']:  # 增加 project_table 中的表项
        p = project_table(project_user_id=data['project_user_id'],
                          project_name=data['project_name'],
                          project_info=data['project_info'],
                          project_dtime=datetime.datetime.now(),
                          project_outpath=config['SURONG_OUT_PATH'],
                          project_status='init')
        db.session.add(p)
        db.session.commit()
        if (p.project_id == None):
            return jsonify({'fault': 'something wrong'}), 500
        else:
            return jsonify({'project_id': p.project_id, 'msg': 'create success'}), 201
    else:  # 更新 project_table 中的表项
        p = project_table.query.get(int(data['project_id']))
        if p:
            p.project_name = data['project_name']
            p.project_info = data['project_info']
        else:
            return jsonify({'fault': 'project_id is not exist'}), 404
        db.session.commit()
        return jsonify({'project_id': p.project_id, 'msg': 'update success'}), 201


# 保存工程接口：projects/save_struture
@projects_bp.route('/save_struture', methods={'POST'})
def save_structure():
    data = request.get_json()
    print(data)
    p = project_table.query.get(int(data['project_id']))

    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404

    # 1. 准备两个列表：old_slst, new_slst
    old_slst = []
    if p.project_structure:
        old_slst = pickle.loads(p.project_structure)
    new_slst = []
    # 2. 依次对每个layer进行处理
    for m in data['project_structure']:
        lid = m.get('layer_id')
        if lid is None:
            return jsonify({'fault': 'can not find layer_id props in project_structure'}), 400
        elif int(lid) == -1:  # 将新模块插入layer_table
            # 创建一个新的layer_obj
            layer_obj = layer_table(layer_project_id=data['project_id'],
                                    layer_x=m.get('layer_x'),
                                    layer_y=m.get('layer_y'),
                                    layer_is_custom=m.get('layer_is_custom'),
                                    layer_param_list=pickle.dumps(m.get('layer_param_list')),
                                    layer_param_num=m.get('layer_param_num'))
            # 检查是否存在 module_id
            layer_module_id = m.get('layer_module_id')
            if layer_module_id is None:
                return jsonify({'fault': 'can not find layer_module_id props in project_structure'}), 400
            # 根据模块类型，将 module_id 赋值给正确的字段
            if bool(m.get('layer_is_custom')):
                layer_obj.layer_cm_id = layer_module_id
            else:
                layer_obj.layer_dm_id = layer_module_id
            # 提交数据库
            db.session.add(layer_obj)
            db.session.commit()
            # 取得新layer的id
            lid = layer_obj.layer_id
        # 将layer_id放入project_table.project_structure
        new_slst.append(lid)
        if old_slst.count(lid):
            old_slst.remove(lid)
    # 3. 将 new_slst 填入p
    p.project_structure = pickle.dumps(new_slst)
    # 4. 将 old_slst 剩余的 layer 从 layer_table 中删去
    for old_layer in old_slst:
        old_layer_obj = layer_table.query.get((old_layer, p.project_id))
        if old_layer_obj:
            db.session.delete(old_layer_obj)
    db.session.commit()
    # 5. 返回响应包
    return jsonify({'project_id': p.project_id, 'project_layer_lst': new_slst}), 201


# 复制工程接口：projects/delete_proj
@projects_bp.route('/delete_proj', methods={'POST'})
def delete_proj():
    config = current_app.config
    data = request.get_json()
    print(data)
    # 用户是否登录的检查 ## 待完成
    # 数据库处理
    p = project_table.query.get(int(data['project_id']))
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404

    # 检查是否为本人删除 ##待完成
    # if session['user_id'] != p.project_user_id:
    #   return jsonify({'fault':'user doesn't match the project'}),403
    # 删除数据库中的工程
    with db.auto_commit_db():
        db.session.delete(p)
    return jsonify({'message': "deleted successfully"}), 200
