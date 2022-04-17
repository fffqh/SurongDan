from flask_sqlalchemy import SQLAlchemy
import flask_mail

# 进行扩展的第一步初始化
db = SQLAlchemy()
mail_obj = flask_mail.Mail()

