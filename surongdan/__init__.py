import os
from tkinter.messagebox import NO
import click
import flask_mail
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from surongdan.views.users import users_bp
from surongdan.views.projects import projects_bp
from surongdan.extensions import db, mail_obj
from surongdan.settings import config
from surongdan.models import user_table

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 工厂函数：创建app
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')  # 实例化app
    app.config.from_object(config[config_name])  # 配置app

    # 注册
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app

# 模块注册
def register_extensions(app):
    db.init_app(app)
    mail_obj.init_app(app)

# 蓝图注册
def register_blueprints(app):
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(projects_bp, url_prefix='/projects')

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
        db.session.commit()
        click.echo("Initialized database.")

    @app.cli.command()
    def dropdb():
        db.drop_all()
        click.echo("Droped database.")


# # app实例化
# app = Flask('surongdan')
# # app配置
# app.config.from_pyfile('settings.py')

# # 扩展模块初始化
# db = SQLAlchemy(app)
# mail_obj = flask_mail.Mail(app)


# from surongdan import views, commands, models
