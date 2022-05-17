from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from surongdan.extensions import db


class user_table(db.Model):
    __tablename__ = 'user_table'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_pwd = db.Column(db.String(120), nullable=False)
    user_status = db.Column(db.Boolean, nullable=False, default=True)
    user_is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<user %d %s %s>' % (self.user_id, self.user_name, self.user_email)

    def set_password(self, password):
        self.user_pwd = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.user_pwd, password)


class project_public_table(db.Model):
    __tablename__ = 'project_public_table'
    project_id = db.Column(db.Integer, db.ForeignKey('project_table.project_id'), primary_key=True)
    project_user_id = db.Column(db.Integer, db.ForeignKey('user_table.user_id'))


class project_table(db.Model):
    __tablename__ = 'project_table'
    # 项目基本信息
    project_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_user_id = db.Column(db.Integer, db.ForeignKey('user_table.user_id'), nullable=False)
    project_name = db.Column(db.String(120), nullable=False)
    project_info = db.Column(db.Text, nullable=True)
    project_dtime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # 项目结构 : 序列化的layer_id
    # project_structure = db.Column(db.PickleType, nullable=True)
    project_layer = db.Column(db.PickleType)
    project_edge = db.Column(db.PickleType)
    # project_node = [node_id, node_id]
    # project_edge = [(from, to),(from, to),(from, to),(from, to)]

    # 输入输出
    project_dataset_id = db.Column(db.Integer, db.ForeignKey('dataset_table.dataset_id'))
    project_outpath = db.Column(db.String(260), nullable=False)
    # 代码和状态
    project_code = db.Column(db.Text, nullable=True)
    project_status = db.Column(db.String(10), nullable=False)
    # 前端样式
    project_json = db.Column(db.Text, nullable=True)
    # 缩略图
    project_image = db.Column(db.Text, nullable=True)


class layer_table(db.Model):
    __tablename__ = 'layer_table'
    # 联合主键 (网络层id, 项目id)
    layer_id = db.Column(db.String(128), primary_key=True)
    layer_project_id = db.Column(db.Integer, db.ForeignKey('project_table.project_id', ondelete='CASCADE'),
                                 primary_key=True)
    # # 是否为自定义模块
    # layer_is_custom = db.Column(db.Boolean, nullable=False, default=False)
    # 自定义模块id
    # layer_cm_id = db.Column(db.Integer, db.ForeignKey('module_custom_table.module_custom_id'))
    # 原型模块id
    layer_module_id = db.Column(db.Integer, db.ForeignKey('module_def_table.module_def_id'))
    # 网络层参数
    layer_param_list = db.Column(db.PickleType, nullable=False)


class module_def_table(db.Model):
    __tablename__ = 'module_def_table'
    module_def_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    module_def_name = db.Column(db.String(120), nullable=False)
    # 模块的使用说明
    module_def_desc = db.Column(db.Text, nullable=False)
    # 模块参数的数量
    module_def_param_num = db.Column(db.Integer, nullable=False)
    module_def_param_name_list = db.Column(db.PickleType, nullable=False)  # [{param_name, isnull, type},{},{}]
    # 模块的代码模板
    module_def_precode = db.Column(db.Text, nullable=False)
    # 是否是用户不可见
    module_def_invisible = db.Column(db.Boolean, nullable=False, default=False)


class module_custom_table(db.Model):
    __tablename__ = 'module_custom_table'
    module_custom_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    module_custom_user_id = db.Column(db.Integer, db.ForeignKey('user_table.user_id'), nullable=False)
    module_custom_name = db.Column(db.String(120), nullable=False)
    # 模块的使用说明
    module_custom_desc = db.Column(db.Text, nullable=False)
    # 前端样式
    module_custom_json = db.Column(db.Text, nullable=True)


class dataset_table(db.Model):
    __tablename__ = 'dataset_table'
    dataset_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    dataset_name = db.Column(db.String(120), nullable=False)
    dataset_desc = db.Column(db.Text, nullable=False)
    dataset_path = db.Column(db.String(260), nullable=False)
