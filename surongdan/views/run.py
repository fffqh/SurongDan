import datetime
import pickle
from flask import current_app
from flask import request, jsonify, Blueprint, session
from sqlalchemy import and_
from concurrent.futures import ThreadPoolExecutor

from surongdan.models import project_table, layer_table, dataset_table, project_superparam_table
from surongdan.precode import *
from surongdan.gencode import *
from surongdan.runcode import *

run_bp = Blueprint('run', __name__)

@run_bp.route('/test_gen_code', methods={'GET'})
def test_gen_code():
    if gen_code(3):
        return jsonify({'msg':'ok'}), 201
    else:
        return jsonify({'fault':'false'}), 500


@run_bp.route('/get_dataset_list', methods={'POST', 'GET'})
def get_dataset_list():
    datas = dataset_table.query.all()
    datalist_data = []
    for dataset in datas:
        datalist_data.append(
            {'dataset_id': dataset.dataset_id,
             'dataset_name': dataset.dataset_name,
             'dataset_desc': dataset.dataset_desc
             }
        )
    return jsonify({'dataset': datalist_data}), 200

@run_bp.route('/run_project', methods={'POST'})
def run_project():
    # 由工程id，获取工程outpath(全路径)
    # 返回值为1: 成功200，文件运行正常，输出正常
    # 返回值为2：成功200，文件运行异常，输出不全(一定有log，但图像不一定)
    # 在运行后，都返回 200 ， Code is running 
    data = request.get_json()
    current_proid = int(data['project_id'])
    current_uid = session.get('user_id')
    print("now user:",current_uid)
    proj_pro = project_table.query.filter(
        and_(project_table.project_id == current_proid, project_table.project_user_id == current_uid)).one_or_none()
    
    if proj_pro is None:
        return jsonify({'fault': 'Project query failed!'}), 404
    else: # status修改为running
        print("find project正在修改")
        with db.auto_commit_db():
            proj_pro.project_status = "running"


    outpath = proj_pro.project_outpath

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(runcode,outpath,current_proid,current_uid)
        print(future.result())

    # 在runcode中修改为done,跑完了
  # 在此之前修改为done,跑完了
    # with db.auto_commit_db():
    #     proj_pro.project_status = "done"
    # return according to output status
    return jsonify({'msg':'Code is running'}), 200

@run_bp.route('/get_output', methods={"GET","POST"})
def get_output():
    data = request.get_json()
    current_proid = int(data['project_id'])
    current_uid = session.get('user_id')
    proj_pro = project_table.query.filter(
        and_(project_table.project_id == current_proid, project_table.project_user_id == current_uid)).one_or_none()
    if proj_pro is None:
        return jsonify({'fault': 'Project query failed!'}), 404
    elif proj_pro.project_status == "init":
        return jsonify({'fault': 'Project has not been run!'}), 403
    print("find project")
    with db.auto_commit_db():
            proj_pro.project_status = "done"
    outpath = proj_pro.project_outpath
    print(outpath)
    code,log,acc,loss = getoutput(outpath)

    if(code!="" and log!="" and acc!="" and loss !=""):
         return jsonify({
             'code': code,
             'log' : log,
             'acc' : acc,
             'loss':loss
         }), 200
    elif(code!="" and log!="" and ((acc!="" and loss !="")==False)):
        return jsonify({
             'code': code,
             'log' : log,
             'acc' : acc,
             'loss':loss
         }), 201
    elif(code!="" and log=="" and ((acc!="" and loss !="")==False)):
        return jsonify({
            'code': code,
            'log' : log,
            'acc' : acc,
            'loss':loss
        }), 202
    else: # 应该不至于发生
            return jsonify({
            'fault': "Other error occurrs"
        }), 405

@run_bp.route('/del_dataset', methods={'POST', 'GET'})
def del_dataset():
    data = request.get_json()
    print(data)
    # 数据正确性检查
    if data.get('dataset_id') is None:
        return jsonify({'fault': 'Bad Data, need dataset_id'}), 400

    p = dataset_table.query.get(int(data['dataset_id']))
    if p is None:
        return jsonify({'fault': 'Dataset is not exist'}), 404
    with db.auto_commit_db():
        db.session.delete(p)
    return jsonify({'msg': 'delete success'}), 200


@run_bp.route('/submit_runinfo', methods={'POST', 'GET'})
def submit_runinfo():
    data = request.get_json()
    print(data)

    if data.get('project_id') is None:
        return jsonify({'fault': 'Bad Data, need project_id'}), 400
    if data.get('dataset_id') is None:
        return jsonify({'fault': 'Bad Data, need dataset_id'}), 400
    if data.get('epoch') is None:
        return jsonify({'fault': 'Bad Data, need epoch'}), 400
    if data.get('learn_rate') is None:
        return jsonify({'fault': 'Bad Data, need learn_rate'}), 400
    if data.get('batch_size') is None:
        return jsonify({'fault': 'Bad Data, need batch_size'}), 400
    if data.get('optimizer') is None:
        return jsonify({'fault': 'Bad Data, need optimizer'}), 400
    if data.get('lossfn') is None:
        return jsonify({'fault': 'Bad Data, need lossfn'}), 400

    p = project_table.query.get(int(data['project_id']))
    if p is None:
        return jsonify({'fault': 'Project is not exist'}), 400

    d = dataset_table.query.get(int(data['dataset_id']))
    if d is None:
        return jsonify({'fault': 'Dataset is not exist'}), 400
    p.project_dataset_id = int(data['dataset_id'])
    db.session.commit()

    param_id = p.project_superparam_id

    if param_id is None:
        temp = project_superparam_table(superparam_epoch=int(data['epoch']),
                                        superparam_batchsize=int(data['batch_size']),
                                        superparam_learnrate=float(data['learn_rate']),
                                        superparam_optim=data['optimizer'],
                                        superparam_lossfn=data['lossfn'])

        with db.auto_commit_db():
            db.session.add(temp)
        p.project_superparam_id = temp.project_superparam_id
        db.session.commit()

        return jsonify({'msg': 'superparam has created'}), 201
    else:
        superpara = project_superparam_table.query.get(int(param_id))
        superpara.superparam_epoch = int(data['epoch'])
        superpara.superparam_batchsize = int(data['batch_size'])
        superpara.superparam_learnrate = float(data['learn_rate'])
        superpara.superparam_optim = data['optimizer']
        superpara.superparam_lossfn = data['lossfn']
        db.session.commit()
        return jsonify({'msg': 'superparam has changed'}), 201
