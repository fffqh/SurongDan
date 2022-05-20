import datetime
import pickle

from flask import current_app
from flask import request, jsonify, Blueprint, session
from sqlalchemy import and_

from surongdan.models import project_table, layer_table
from surongdan.precode import *

projects_bp = Blueprint('projects', __name__)


# 测试 gen_precode
@projects_bp.route('/test_genprecode', methods={'POST'})
def test_genprecode():
    data = request.get_json()
    precode = gen_precode(data['module_custom_structure'])
    return jsonify({'precode': precode}), 200


# 保存工程接口：projects/save_projinfo
@projects_bp.route('/save_projinfo', methods={'POST'})
def save_projinfo():
    config = current_app.config
    data = request.get_json()
    print(data)
    # 用户是否登录的检查 ## 待完成
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'msg': 'please login!'}), 403
    # 数据库处理
    if data['project_is_new']:  # 增加 project_table 中的表项
        p = project_table(project_user_id=int(user_id),
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


# 保存工程接口：projects/save_structure
@projects_bp.route('/save_structure', methods={'POST'})
def save_structure():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    if data.get('project_layers') is None:
        return jsonify({'fault': 'Bad Data, need project_layers'}), 400
    if data.get('project_edges') is None:
        return jsonify({'fault': 'Bad Data, need project_edges'}), 400
    if data.get('project_json') is None:
        return jsonify({'fault': 'Bad Data, need project_json'}), 400
    if data.get('project_image') is None:
        return jsonify({'fault': 'Bad Data, need project_image'}), 400

    # 数据库中查项目
    p = project_table.query.get(int(data['project_id']))
    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404

    # 进入一个数据库事务
    with db.auto_commit_db():
        # 读取项目中所有旧的layer，把它们都删掉！
        players = p.layers.all()
        for player in players:
            db.session.delete(player)
        # 准备一个 layer_id_list
        layer_id_list = []
        # 插入新的layer到数据库中，逐个处理
        for layer in data['project_layers']:
            if layer.get('layer_id') is None:
                return jsonify({'fault': 'Bad Data, need layer_id'}), 400
            if layer.get('layer_module_id') is None:
                return jsonify({'fault': 'Bad Data, need layer_module_id'}), 400
            if layer.get('layer_param') is None:
                return jsonify({'fault': 'Bad Data, need layer_param'}), 400
                # 数据库中查该layer对应的module
            layer_module = module_def_table.query.get(int(layer.get('layer_module_id')))
            if layer_module is None:
                return jsonify({'fault': 'Bad Data, layer_module_id is invalid'}), 400
                # 得到该 module 所需的参数列表
            def_param_list = pickle.loads(layer_module.module_def_param_name_list)
            # 准备空的参数列表
            layer_param_list = []
            for defp in def_param_list:
                name = defp.get('name')
                type = defp.get('type')
                isnull = defp.get('isnull')
                defv = defp.get('value')
                if (name is None) or (type is None) or (isnull is None):
                    return jsonify({'fault': 'Bad DataBase, module_def_param_name_list is invalid'}), 400
                    # 检查request data中是否有该参数
                param = layer['layer_param'].get(str(name))
                if param is None and (not bool(isnull)):
                    return jsonify({'fault': 'layer_param error, need {}'.format(str(name))}), 400
                    # 有的，进行更新
                if param:
                    layer_param_list.append(param)
                else:
                    layer_param_list.append(defv)
            new_layer = layer_table(layer_id=str(layer['layer_id']),
                                    layer_project_id=p.project_id,
                                    layer_module_id=int(layer['layer_module_id']),
                                    layer_param_list=pickle.dumps(layer_param_list))
            db.session.add(new_layer)
            layer_id_list.append(new_layer.layer_id)
        p.project_layer = pickle.dumps(layer_id_list)
        # 对project_edges字段进行检查 ：1. 不能出现孤立点；2. 不能成环（待完成）
        p.project_edge = pickle.dumps(data['project_edges'])
        p.project_image = data['project_image']
        p.project_json = data['project_json']

    return jsonify({'msg': 'ok'}), 201


# 复制工程接口：projects/copy_proj
@projects_bp.route('/copy_proj', methods={'POST'})
def copy_proj():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    # 用户是否登录的检查 #
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403
    p = project_table.query.get(int(data['project_id']))
    # 检查项目是否存在
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404
    # 用户是否是被复制项目拥有者的检查
    # if session.get('user_id') != p.project_user_id:
    #    return jsonify({'fault': 'user does not match the project'}), 403

    # 对新项进行赋值
    new_p = project_table(project_user_id=p.project_user_id,
                          project_name=p.project_name + ' - 副本',
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
                old_layer = layer_table.query.get([int(project_layer[i]), p.project_id])
                new_layer = layer_table(layer_id=old_layer.layer_id,
                                        layer_project_id=new_p.project_id,
                                        layer_module_id=old_layer.layer_module_id,
                                        layer_param_list=old_layer.layer_param_list
                                        )
                db.session.add(new_layer)

    # if new_p.project_id is None:
    #     return jsonify({'fault': 'new project failed'}), 500
    # # 更新project的结构数据
    # lay_list = []
    # for m in layer_obj:
    #     if m.layer_id is None:
    #         return jsonify({'fault': 'new layer failed'}), 500
    #     lay_list.append(m.layer_id)
    # # 内部存在结构，则保存
    # if len(lay_list) != 0:
    #     with db.auto_commit_db():
    #         new_p.project_structure = pickle.dumps(lay_list)
    return ({'project_id': new_p.project_id, 'msg': 'copy success'}), 201


# 删除工程接口：projects/delete_proj
@projects_bp.route('/delete_proj', methods={'POST'})
def delete_proj():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    # 用户是否登录的检查 #
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403

    # 数据库处理
    p = project_table.query.get(int(data['project_id']))
    if p is None:
        return jsonify({'fault': 'project_id is not exist'}), 404
    # 检查是否为本人删除
    # if session.get('user_id') != p.project_user_id:
    #    return jsonify({'fault': 'user does not match the project'}), 403
    # 删除数据库中的工程
    with db.auto_commit_db():
        db.session.delete(p)
    return jsonify({'msg': "delete successful"}), 200


# 获得工程列表接口
@projects_bp.route('/getlist', methods={'GET'})
def getlist():
    # 在登录成功之后记录用户信息到session
    # 查询project_table到所有user_id相同者创建的项目
    current_uid = session.get("user_id")
    # print(current_uid)
    proj_list = project_table.query.with_entities(project_table.project_id).filter(
        project_table.project_user_id == current_uid).all()
    plst = []
    for p in proj_list:
        plst.append(p.project_id)
    if proj_list != None:
        return jsonify({'proj_list': plst}), 200
    else:
        return jsonify({'fault': 'Projects are not exist'}), 403


# 获得工程
@projects_bp.route('/getproj', methods={'POST'})
def getproj():
    # 在登录成功之后记录用户信息到session
    # 查询project_table到所有user_id相同者创建的项目
    print("---")
    data = request.get_json()
    print(data)  # using for debug
    current_proid = int(data['proj_id'])
    current_uid = session.get('user_id')
    #     proj_pro = project_table.query_pro(current_uid, current_proid)
    proj_pro = project_table.query.filter(
        and_(project_table.project_id == current_proid, project_table.project_user_id == current_uid)).one_or_none()
    #
    if proj_pro != None:
        #         lid_lst = []
        #         if proj_pro.project_structure:
        #             layer_lst = pickle.loads(proj_pro.project_structure)
        #             for lid in layer_lst:
        #                 lid_lst.append(lid)

        return jsonify({'project_id': proj_pro.project_id,
                        'project_user_id': proj_pro.project_user_id,
                        'project_name': proj_pro.project_name,
                        'project_info': proj_pro.project_info,
                        'project_dtime': proj_pro.project_dtime,
                        #                         'project_dataset_id': proj_pro.project_dataset_id,
                        #                         'project_outpath': proj_pro.project_outpath,
                        #                         'project_code': proj_pro.project_code,
                        #                         'project_status': proj_pro.project_status,
                        'project_json': proj_pro.project_json,
                        'project_image': proj_pro.project_image}), 200
    else:
        return jsonify({'fault': 'Projects are not accessible'}), 403


# 添加默认模块：projects/add_def_md
@projects_bp.route('/add_def_md', methods={'POST'})
def add_def_md():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('module_def_name') is None:
        return jsonify({'fault': 'Bad Data, need module_def_name'}), 400
    if data.get('module_def_desc') is None:
        return jsonify({'fault': 'Bad Data, need module_def_desc'}), 400
    if data.get('module_def_param') is None:
        return jsonify({'fault': 'Bad Data, need module_def_param'}), 400
    if data.get('module_def_precode') is None:
        return jsonify({'fault': 'Bad Data, need module_def_precode'}), 400
    for param in data['module_def_param']:
        name = param.get('name')
        type = param.get('type')
        isnull = param.get('isnull')
        defv = param.get('value')
        if (name is None) or (type is None) or (isnull is None):
            return jsonify({'fault': 'Bad Data, module_def_param is invalid'}), 400
        if defv is None and (not bool(isnull)):
            return jsonify({'fault': 'Bad Data, {} need def_value'.format(str(name))}), 400
    # 用户是否登录的检查
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403
    # 用户是否为管理员账号的检查
    # if not session.get('user_is_admin'):
    #    return jsonify({'fault': 'User is not an administrator'}), 403
    # 数据库处理
    p = module_def_table(module_def_name=data['module_def_name'],
                         module_def_desc=data['module_def_desc'],
                         module_def_param_num=len(data['module_def_param']),
                         module_def_param_name_list=pickle.dumps(data['module_def_param']),
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
    # 数据正确性检查
    if data.get('module_def_id') is None:
        return jsonify({'fault': 'Bad Data, need module_def_id'}), 400
    # 用户是否登录的检查
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403
    # 用户是否为管理员账号的检查
    # if not session.get('user_is_admin'):
    #    return jsonify({'fault': 'User is not an administrator'}), 403
    # 数据库处理
    p = module_def_table.query.get(int(data['module_def_id']))
    if p is None:
        return jsonify({'fault': 'def_module is not exist'}), 404

    # 更改可见性
    with db.auto_commit_db():
        p.module_def_invisible = True
    return jsonify({'msg': 'delete success'}), 200


# 添加自定义模块：/projects/add_cus_md
@projects_bp.route('/add_cus_md', methods={'POST'})
def add_cus_md():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('module_custom_user_id') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_user_id'}), 400
    if data.get('module_custom_name') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_name'}), 400
    if data.get('module_custom_desc') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_desc'}), 400
    if data.get('module_custom_json') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_json'}), 400
    # 用户是否登录的检查 #
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403
    # 数据库处理
    p = module_custom_table(module_custom_user_id=session.get('user_id'),
                            module_custom_name=data['module_custom_name'],
                            module_custom_desc=data['module_custom_desc'],
                            module_custom_json=data['module_custom_json']
                            )

    # 更新数据库
    with db.auto_commit_db():
        db.session.add(p)
    if p.module_custom_id is None:
        return jsonify({'fault': 'something wrong'}), 500
    else:
        return jsonify({'module_custom_id': p.module_custom_id, 'msg': 'create success'}), 201


# 更改自定义模块信息：/projects/edit_cus_md
@projects_bp.route('/edit_cus_md', methods={'POST'})
def edit_cus_md():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('module_custom_id') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_id'}), 400
    if data.get('module_custom_name') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_name'}), 400
    if data.get('module_custom_desc') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_desc'}), 400
    # 用户是否登录的检查 #
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403

    # 数据库处理
    p = module_custom_table.query.get(int(data['module_custom_id']))
    # 检查自定义模块是否存在并可见
    if p is None:
        return jsonify({'fault': 'module_custom_id is not exist'}), 404
    # 用户是否是模块的拥有者的检查 #
    # if p.module_custom_user_id != session.get('user_id'):
    #    return jsonify({'fault': 'user does not match the module'}), 403
    # 更新数据库
    with db.auto_commit_db():
        p.module_custom_name = data['module_custom_name']
        p.module_custom_desc = data['module_custom_desc']
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
    # 数据正确性检查
    if data.get('module_custom_id') is None:
        return jsonify({'fault': 'Bad Data, need module_custom_id'}), 400
    # 数据库处理
    p = module_custom_table.query.get(int(data['module_custom_id']))
    if p is None:
        return jsonify({'fault': 'def_module is not exist'}), 404
    # 用户是否登录的检查 #
    # if not session.get('logged_in'):
    #    return jsonify({'fault': 'you have not logged in'}), 403
    # 用户是否是模块的拥有者的检查 #
    # if p.module_custom_user_id != session.get('user_id'):
    #    return jsonify({'fault': 'user does not match the module'}), 403
    # 更改可见性
    with db.auto_commit_db():
        db.session.delete(p)
    return jsonify({'msg': 'delete success'}), 200


# 获取默认模块：projects/get-def-cos-module
# 加载时，作为侧边栏的基础元素出现
@projects_bp.route('/get_def_module', methods={'GET'})
def get_def_md():
    datas = module_def_table.query.filter_by(module_def_invisible=False)
    # print(datas)
    def_data = []
    for defs in datas:
        def_data.append({'module_def_id': defs.module_def_id, 'module_def_name': defs.module_def_name,
                         'module_def_param_num': defs.module_def_param_num})
    return jsonify({'def_data': def_data})


@projects_bp.route('/get_custom_module', methods={'GET'})
def get_cus_md():
    u_id = session.get('user_id')
    datas = module_custom_table.query.filter_by(module_custom_invisible=False, module_custom_user_id=u_id).all()
    cos_data = []
    for coss in datas:
        cos_data.append(
            {'module_custom_id': coss.module_custom_id, 'module_custom_name': coss.module_custom_name,
             'module_custom_desc': coss.module_custom_desc, 'module_custom_param_num': coss.module_custom_param_num,
             'module_custom_json': coss.module_custom_json}
        )
    return jsonify({'cos_data': cos_data}), 201


# 生成代码
@projects_bp.route('/generatecode', methods={'POST'})
def generate_code():
    # 获得json中的项目id
    data = request.get_json()
    pro_id = int(data['project_id'])
    p = project_table.query.get(pro_id)
    if p is None:
        return jsonify({'msg': 'project is not exist !'})

    # 读取struct结构
    pro_struct = pickle.loads(p.project_structure)
    print(pro_struct)
    # 准备数据集??
    # data_set_id = p.project_dataset_id
    # data_set = dataset_table.query.filter(dataset_table.dataset_id == data_set_id)
    # data_set_path = str(data_set['dataset_path'])
    # code集合
    pro_code = ''
    # 输出结果路径
    pro_outpath = str(p.project_outpath)
    # 遍历struct查找layer_id
    for layer_id in pro_struct:
        layer_now = layer_table.query.get(layer_id)
        if layer_now is None:
            return jsonify({'fault': 'The layer is not exist'}), 402
        if int(layer_now.layer_param_num) != len(layer_now.layer_param_list):
            return jsonify({'fault': 'Parameters is inconsistent with the input module'}), 401
        # 读取参数
        layer_n_para = layer_now.layer_param_list
        if not layer_now.layer_is_custom:
            # 默认模块处理
            layer_mod_id = int(layer_now.layer_dm_id)
            layer_mod = module_def_table.query.get(layer_mod_id)
            if len(layer_now.param_list) != len(layer_mod.module_def_param_num):
                return jsonify({'fault': 'Layer_para is inconsistent with the module_para'}), 402
            layer_n_code = ''
            layer_n_code = str(layer_mod.module_def_code)
            for paras in layer_n_para:
                # 默认参数不大于10个
                layer_n_code = re.sub(r'\$[0-9]', str(paras), layer_n_code, 1)
        else:
            # 自定义模块
            layer_mod_id = layer_now.layer_cm_id
            layer_mod = module_custom_table.query.get(layer_mod_id)
            if len(layer_now.param_list) != len(layer_mod.module_cus_param_num):
                return jsonify({'fault': 'Layer_para is inconsistent with the module_para'}), 402
            layer_n_code = ''
            layer_n_code = str(layer_mod.module_cus_code)
            for paras in layer_n_para:
                # 默认参数不大于10个
                layer_n_code = re.sub(r'\$[0-9]', str(paras), layer_n_code, 1)
        # 当前layer生成的代码进行保存
        pro_code = pro_code + layer_n_code + "\n"
    # 讲生成的代码进行保存到输出路径
    fb = open(pro_outpath + 'outfile.txt', mode='w', encoding='utf-8')
    fb.write(pro_code)
    fb.close()
    return jsonify({'msg': 'Generate Successful ! At' + pro_outpath + 'outfile.txt'}), 200
