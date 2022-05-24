import datetime
import pickle
from flask import current_app
from flask import request, jsonify, Blueprint, session
from sqlalchemy import and_

from surongdan.models import project_table, layer_table,dataset_table,project_superparam_table
from surongdan.precode import *

run_bp = Blueprint('run', __name__)



@run_bp.route('/get_dataset_list', methods={'POST','GET'})
def get_dataset_list():
    datas = dataset_table.query.all()
    datalist_data = []
    for dataset in datas:
        datalist_data.append(
            {'dataset_id': dataset.dataset_id,
             'dataset_name': dataset. dataset_name,
             'dataset_desc': dataset.dataset_desc
             }
        )
    return jsonify({'dataset_list': datalist_data}), 201

@run_bp.route('/del_dataset', methods={'POST','GET'})
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

@run_bp.route('/submit_runinfo', methods={'POST','GET'})
def del_dataset():
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

    param_id = p.project_superparam_id

    superpara = project_superparam_table.query.get(int(param_id))

    if superpara is None:
        temp = project_superparam_table(superparam_epoch=int(data['epoch']),
                                        superparam_batchsize=int(data['batch_size']),
                                        superparam_learnrate=float(data['learn_rate']),
                                        superparam_optim=data['optimizer'],
                                        superparam_lossfn=data['lossfn'])
        with db.auto_commit_db():
            db.session.add(temp)
        return jsonify({'superparam has changed'}), 201
    else:
        superpara.superparam_epoch = int(data['epoch'])
        superpara.superparam_batchsize=int(data['batch_size'])
        superpara.superparam_learnrate=float(data['learn_rate'])
        superpara.superparam_optim=data['optimizer']
        superpara.superparam_lossfn=data['lossfn']
        db.session.commit()
        return jsonify({'superparam has saved'}), 201
