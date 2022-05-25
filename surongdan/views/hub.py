import pickle

from flask import request, jsonify, Blueprint, session

from surongdan.extensions import db
from surongdan.models import project_table, layer_table, project_public_table, user_table

hub_bp = Blueprint('hub', __name__)


# 发布创意接口：/hub/get_list
@hub_bp.route('/get_list', methods={'GET'})
def get_list():
    # 用户是否登录的检查 #
    if not session.get('logged_in'):
        return jsonify({'fault': 'you have not logged in'}), 403
    project_list = project_public_table.query.all()
    plst = []
    for proj in project_list:
        p = project_table.query.get(proj.project_id)
        u = user_table.query.get(proj.project_user_id)
        plst.append({"project_id": p.project_id,
                      "project_name": p.project_name,
                      "project_desc": p.project_info,
                      "project_user_name": u.user_name,
                      "project_image": p.project_image
                      })
    return jsonify({"plst": plst}), 200


# 发布创意接口：/hub/set_public
@hub_bp.route('/set_public', methods={'POST'})
def set_public():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    # 用户是否登录的检查 #
    if not session.get('logged_in'):
        return jsonify({'fault': 'you have not logged in'}), 403
    public_p = project_public_table.query.get(int(data['project_id']))
    # 检查项目是否公开
    if public_p:
        return jsonify({'fault': 'project is already public'}), 400
    p = project_table.query.get(int(data['project_id']))
    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404
    # 用户是否是被复制项目拥有者的检查
    if session.get('user_id') != p.project_user_id:
        return jsonify({'fault': 'user does not match the project'}), 403

    # 对新项进行赋值
    public_p = project_public_table(project_id=p.project_id,
                                    project_user_id=p.project_user_id)
    with db.auto_commit_db():
        db.session.add(public_p)
    return jsonify({'msg': 'set public success'}), 200


# 删除创意接口：/hub/set_private
@hub_bp.route('/set_private', methods={'POST'})
def set_private():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    # 用户是否登录的检查 #
    if not session.get('logged_in'):
        return jsonify({'fault': 'you have not logged in'}), 403
    public_p = project_public_table.query.get(int(data['project_id']))
    # 检查项目是否公开
    if public_p is None:
        return jsonify({'fault': 'project_id is not public'}), 400
    p = project_table.query.get(int(data['project_id']))
    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404
    # 用户是否是被复制项目拥有者的检查
    if session.get('user_id') != p.project_user_id:
        return jsonify({'fault': 'user does not match the project'}), 403

    # 对数据库进行操作
    with db.auto_commit_db():
        db.session.delete(public_p)
    return jsonify({'msg': 'set private success'}), 200


# 转存工程接口：/hub/fork
@hub_bp.route('/fork', methods={'POST'})
def fork():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    # 用户是否登录的检查 #
    if not session.get('logged_in'):
        return jsonify({'fault': 'you have not logged in'}), 403
    p = project_public_table.query.get(int(data['project_id']))
    # 检查项目是否公开
    if p is None:
        return jsonify({'fault': 'project_id is not public'}), 404
    p = project_table.query.get(int(data['project_id']))
    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404

    # 对新项进行赋值
    new_p = project_table(project_user_id=session.get('user_id'),
                          project_name=p.project_name,
                          project_info=p.project_info,
                          project_dtime=p.project_dtime,
                          project_layer=p.project_layer,
                          project_edge=p.project_edge,
                          project_dataset_id=p.project_dataset_id,
                          project_outpath=p.project_outpath,
                          project_code=p.project_code,
                          project_status=p.project_status,
                          project_json=p.project_json,
                          project_image=p.project_image)

    # 提交数据库，project的提交与layer一起进行，方便进行回滚,避免出现失效的project数据
    with db.auto_commit_db():
        db.session.add(new_p)
        # 依次新建所有的layer
        # layer_obj = []  # 存储layer的列表，之后一次性提交所有的数据库更改，便于回滚
        if p.project_layer is not None:
            project_layer = pickle.loads(p.project_layer)
            for i in range(len(project_layer)):
                old_layer = layer_table.query.get([project_layer[i], p.project_id])
                new_layer = layer_table(layer_id=old_layer.layer_id,
                                        layer_project_id=new_p.project_id,
                                        layer_module_id=old_layer.layer_module_id,
                                        layer_param_list=old_layer.layer_param_list
                                        )
                db.session.add(new_layer)

    return jsonify({'project_id': new_p.project_id, 'msg': 'copy success'}), 200
