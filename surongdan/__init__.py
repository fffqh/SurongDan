import os
from tkinter.messagebox import NO
import click
import flask_mail
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from surongdan.views.vue import vue_bp
from surongdan.views.users import users_bp
from surongdan.views.projects import projects_bp
from surongdan.views.run import run_bp
from surongdan.views.hub import hub_bp
from surongdan.extensions import db, mail_obj
from surongdan.settings import config
from surongdan.models import module_def_table, user_table, project_table,dataset_table

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 工厂函数：创建app
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    app = Flask('bluelog')  # 实例化app    
    if config_name == 'testing':
        app.config[ 'SERVER_NAME' ] = "localhost.localdomain:5000"
   
    app.config.from_object(config[config_name])  # 配置app
    if config_name == 'testing':
        app.config[ 'SERVER_NAME' ] = "localhost.localdomain:5000"
    # 注册
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    # 创建code目录
    mk_codedir(app)
    return app

# 创建code目录
def mk_codedir(app):
    if(not os.path.exists(app.config['SURONG_OUT_PATH'])):
        os.mkdir(app.config['SURONG_OUT_PATH'])

# 模块注册
def register_extensions(app):
    db.init_app(app)
    mail_obj.init_app(app)

# 蓝图注册
def register_blueprints(app):
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(run_bp,url_prefix='/run')
    app.register_blueprint(hub_bp,url_prefix='/hub')
    app.register_blueprint(vue_bp, url_prefix='')

# 命令注册
def register_commands(app):
    @app.cli.command()
    def initdb():
        db.create_all()
        u = user_table(user_name='admin',
                       user_email='admin@qq.com',
                       user_status=True,
                       user_is_admin=True)
        u.set_password('admin123')
        db.session.add(u)
        u = user_table(user_name='user',
                       user_email='user@qq.com',
                       user_status=True,
                       user_is_admin=False)
        u.set_password('user123')
        db.session.add(u)
        db.session.commit()
        ## 添加默认模块 conv2d，pooling2d，linear，relu
        # m1 = module_def_table(  module_def_name='conv_layer',
        #                         module_def_desc='conv2d卷积层',
        #                         module_def_param_num=11,
        #                         module_def_precode='nn.Conv2d($0, $1, $2, stride=$3, padding=$4, dilation=$5, groups=$6, bias=$7, padding_mode=$8, device=$9, dtype=$10)'
        #                         )
        # m2 = module_def_table(  module_def_name='pooling_layer',
        #                         module_def_desc='pooling2d池化层',
        #                         module_def_param_num=6,
        #                         module_def_precode='torch.nn.AvgPool2d($0, stride=$1, padding=$2, ceil_mode=$3, count_include_pad=$4, divisor_override=$5)'
        #                         )
        # m3 = module_def_table(  module_def_name='fc_layer',
        #                         module_def_desc='linear卷积层',
        #                         module_def_param_num=5,
        #                         module_def_precode='nn.Linear($0, $1, bias=$2, device=$3, dtype=$4)'
        #                         )
        # m4 = module_def_table(  module_def_name='activate_function',
        #                         module_def_desc='relu激活函数',
        #                         module_def_param_num=1,
        #                         module_def_precode='nn.ReLU(inplace=$0)'
        #                         )
        # db.session.add(m1)
        # db.session.add(m2)
        # db.session.add(m3)
        # db.session.add(m4)
        # db.session.commit()
        dataset = dataset_table(
            dataset_name = 'MINIST',
            dataset_desc = 'Normal dataset',
            dataset_path = 'null'
        )
        proj = project_table(
                project_user_id = 1,
                project_name = 'a proj',
                project_info ='',
                project_layer = '',
                project_edge = '',
                # 输入输出
                project_dataset_id = '1',
                project_outpath = 'E:\Github\SoftwareSever\surong_dan_server\out',
                # 代码和状态
                project_code = '',
                project_status = 'init'
        )
        db.session.add(dataset)
        db.session.commit()
        db.session.add(proj)
        db.session.commit()

        click.echo("Initialized database.")

    @app.cli.command()
    def dropdb():
        db.drop_all()
        click.echo("Droped database.")


#     暂时无法使用，直接运行python tests/__init__.py即可
    @app.cli.command()
    def test():
        import unittest
        import sys
#         sys.path.append("..")
        tests = unittest.TestLoader().discover("./tests")
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        if result.errors or result.failures:
            sys.exit(1)

# # app实例化
# app = Flask('surongdan')
# # app配置
# app.config.from_pyfile('settings.py')

# # 扩展模块初始化
# db = SQLAlchemy(app)
# mail_obj = flask_mail.Mail(app)


# from surongdan import views, commands, models
