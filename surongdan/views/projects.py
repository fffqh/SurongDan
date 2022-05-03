import datetime
import pickle

from flask import current_app
from flask import request, jsonify, Blueprint,g

from surongdan.extensions import db
from surongdan.models import project_table, layer_table, module_def_table, module_custom_table

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


# 复制工程接口：projects/copy_proj
@projects_bp.route('/copy_proj', methods={'POST'})
def copy_proj():
    data = request.get_json()
    print(data)
    # 用户是否登录的检查 ## 待完成
    p = project_table.query.get(int(data['project_id']))
    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404
    # 用户是否是被复制项目拥有者的检查 ##待检查
    # if session['user_id'] != p.project_user_id:
    #   return jsonify({'fault':'user doesn't match the project'}),403

    # 对新项进行赋值
    new_p = project_table(project_user_id=p.project_user_id,
                          project_name=p.project_name + ' - 副本',
                          project_info=p.project_info,
                          project_dtime=p.project_dtime,
                          project_dataset_id=p.project_dataset_id,
                          project_outpath=p.project_outpath,
                          project_code=p.project_code,
                          project_status=p.project_status)

    project_structure = pickle.loads(p.project_structure)
    # 依次新建所有的layer
    layer_obj = []  # 存储layer的列表，之后一次性提交所有的数据库更改，便于回滚
    for i in range(len(project_structure)):
        old_layer = layer_table.query.get(int(project_structure[i]))
        new_layer = layer_table(layer_x=old_layer.layer_x,
                                layer_y=old_layer.layer_y,
                                layer_is_custom=old_layer.layer_is_custom,
                                layer_cm_id=old_layer.layer_cm_id,
                                layer_dm_id=old_layer.layer_dm_id,
                                layer_param_list=old_layer.layer_param_list,
                                layer_param_num=old_layer.layer_param_num,

                                )
        layer_obj.append(new_layer)
    # 提交数据库，project的提交与layer一起进行，方便进行回滚,避免出现失效的project数据
    with db.auto_commit_db():
        db.session.add(new_p)
        for m in layer_obj:
            db.session.add(m)
            m.layer_project_id = new_p.project_id

    if new_p.project_id is None:
        return jsonify({'fault': 'new project failed'}), 500
    # 更新project的结构数据
    lay_list = []
    for m in layer_obj:
        if m.layer_id is None:
            return jsonify({'fault': 'new layer failed'}), 500
        lay_list.append(m.layer_id)
    with db.auto_commit_db():
        new_p.project_structure = pickle.dumps(lay_list)
    return ({'project_id': new_p.project_id, 'msg': 'copy success'}), 201


# 删除工程接口：projects/delete_proj
@projects_bp.route('/delete_proj', methods={'POST'})
def delete_proj():
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
    return jsonify({'msg': "delete successful"}), 200


# 添加默认模块：projects/add_def_md
@projects_bp.route('/add_def_md', methods={'POST'})
def add_def_md():
    data = request.get_json()
    print(data)
    # 用户是否登录的检查以及用户是否为管理员账号的检查 ## 待完成
    # u = user_table.query.get(int(session['user_id']))
    # if not u.user_is_admin:
    #    return jsonify({'fault': 'User is not an administrator'}), 403
    # 数据库处理
    p = module_def_table(module_def_name=data['module_def_name'],
                         module_def_desc=data['module_def_desc'],
                         module_def_param_num=data['module_def_param_num'],
                         module_def_precode=data['module_def_precode']
                         )
    with db.auto_commit_db():
        db.session.add(p)
    if p.module_def_id is None:
        return jsonify({'fault': 'something wrong'}), 500
    else:
        return jsonify({'module_def_id': p.module_def_id, 'msg': 'create success'}), 201


# 删除默认模块：projects/delete_def_md
# 并非实际删除，而是将其设定为用户不可见
@projects_bp.route('/delete_def_md', methods={'POST'})
def delete_def_md():
    data = request.get_json()
    print(data)
    # 用户是否登录的检查以及用户是否为管理员账号的检查 ## 待完成
    # u = user_table.query.get(int(session['user_id']))
    # if not u.user_is_admin:
    #    return jsonify({'fault': 'User is not an administrator'}), 403
    # 数据库处理
    p = module_def_table.query.get(int(data['module_def_id']))
    if p is None:
        return jsonify({'fault': 'def_module is not exist'}), 404

    # 更改可见性
    with db.auto_commit_db():
        p.module_def_invisible = True
    return jsonify({'msg': 'delete success'}), 200


# 获得工程列表接口
@projects_bp.route('/getlist', methods={'GET'})
def getlist():
    # 在登录成功之后记录用户信息到flask.g.user
    # 查询project_table到所有user_id相同者创建的项目
    current_uid = g.user.user_id
    proj_list = project_table.query_prolist(current_uid)
    if proj_list!=None:
        return jsonify({'project_list': proj_list}), 201
    else:
        return jsonify({'fault': 'Projects are not exist'}), 403

# 获得工程
@projects_bp.route('/getproj', methods={'GET'})
def getproj():
    # 在登录成功之后记录用户信息到全局flask.g.user
    # 查询project_table到所有user_id相同者创建的项目
    data = request.get_json()
    print(data)# using for debug
    current_proid = int(data['project_id'])
    current_uid = g.user.user_id
    proj_pro = project_table.query_pro(current_uid,current_proid)
    if proj_pro!=None:
        return jsonify({'project_id' : proj_pro.project_id,
                        'project_user_id':proj_pro.project_user_id,
                        'project_name':proj_pro.project_name,
                        'project_info':proj_pro.project_info,
                        'project_dtime':proj_pro.project_dtime,
                        'project_structure':proj_pro.project_structure,
                        'project_dataset_id':proj_pro.project_dataset_id,
                        'project_outpath':proj_pro.project_outpath,
                        'project_code':proj_pro.project_code,
                        'project_status':proj_pro.project_status}), 200
    else:
        return jsonify({'fault': 'Projects are not accessible'}), 403


# 添加自定义模块：/projects/add_cus_md
@projects_bp.route('/add_cus_md', methods={'POST'})
def add_cus_md():
    data = request.get_json()
    print(data)
    # 用户是否登录的检查 ## 待完成
    # 数据库处理
    p = module_custom_table(module_custom_user_id=data['module_custom_user_id'],
                            # module_custom_user_id=session['user_id'],
                            module_custom_name=data['module_custom_name'],
                            module_custom_desc=data['module_custom_desc'],
                            module_custom_param_num=data['module_custom_param_num']
                            )
    # 判断结构是否正确
    para_sum = 0
    for m in data['module_custom_struture']:
        if m['module_is_custom']:
            mp = module_custom_table.query.get(int(m['module_id']))
        else:
            mp = module_def_table.query.get(int(m['module_id']))
        # 无对应模块
        if mp is None:
            return jsonify({'fault': 'The included module does not exist'}), 400
        # 模块不可被调用
        if m['module_is_custom'] and mp.module_custom_invisible:
            return jsonify({'fault': 'the module is invisible'}), 400
        elif not m['module_is_custom'] and mp.module_def_invisible:
            return jsonify({'fault': 'the module is invisible'}), 400
        # 模块参数个数与请求的参数个数不符
        if m['module_is_custom'] and mp.module_custom_param_num != len(m['module_param_list']):
            return jsonify({'fault': 'Parameter number does not match'}), 400
        elif not m['module_is_custom'] and mp.module_def_param_num != len(m['module_param_list']):
            return jsonify({'fault': 'Parameter number does not match'}), 400
        para_sum += len(m['module_param_list'])
    # 总参数个数是否符合
    if para_sum != data['module_custom_param_num']:
        return jsonify({'fault': 'The total number of parameters does not match'}), 400
    # 将模块结构转化为pickle存储
    p.module_custom_struture = pickle.dumps(data['module_custom_struture'])
    # 更新数据库
    with db.auto_commit_db():
        db.session.add(p)
    if p.module_custom_id is None:
        return jsonify({'fault': 'something wrong'}), 500
    else:
        return jsonify({'module_custom_id': p.module_custom_id, 'msg': 'create success'}), 201


# 删除自定义模块：projects/delete_cus_md
# 并非实际删除，而是将其设定为用户不可见
@projects_bp.route('/delete_cus_md', methods={'POST'})
def delete_cus_md():
    data = request.get_json()
    print(data)
    # 数据库处理
    p = module_custom_table.query.get(int(data['module_custom_id']))
    if p is None:
        return jsonify({'fault': 'def_module is not exist'}), 404
    # 用户是否是模块的拥有者的检查 ## 待完成
    # if p.module_custom_user_id != session['user_id']:
    #    return jsonify({'fault': 'user doesn't match the module'}), 403
    # 更改可见性
    with db.auto_commit_db():
        p.module_custom_invisible = True
    return jsonify({'msg': 'delete success'}), 200

