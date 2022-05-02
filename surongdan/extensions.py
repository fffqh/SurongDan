from contextlib import contextmanager

import flask_mail
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy


# 自定义一个SQLAlchemy集成flask_sqlalchemy,便于自定义方法
# 用例如下,添加一行数据p：
# with db.auto_commit_db():
#   db.session.add(p)
class SQLAlchemy(BaseSQLAlchemy):
    # 利用contextmanager对try/except语句进行封装，使用时要与with结合
    @contextmanager
    def auto_commit_db(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            # 提交失败，必须进行回滚
            self.session.rollback()
            raise e


# 进行扩展的第一步初始化
db = SQLAlchemy()
mail_obj = flask_mail.Mail()
