from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
import flask_mail

# app实例化
app = Flask('surongdan')
# app配置
app.config.from_pyfile('settings.py')

# 扩展模块初始化
db = SQLAlchemy(app) 
mail_obj = flask_mail.Mail(app)


from surongdan import views, commands, models

