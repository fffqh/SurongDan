import os
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    # 程序秘钥
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    # SMTP服务器地址
    MAIL_SERVER = 'smtp.163.com'
    # SMTP服务器端口，一般为465
    MAIL_PORT = 465
    # 是否启用SSL加密
    MAIL_USE_SSL = True
    # 是否启用TLS加密
    MAIL_USE_TLS = False
    # 登入的邮箱，例如2731510961@qq.com，不能使用无法其他服务的邮箱，例如snbckcode@gmail.com不能使用smtp.qq.com
    MAIL_USERNAME = 'exten224@163.com'
    # 授权码，在设置smtp的时候有
    MAIL_PASSWORD = 'WWLXZTCBXMLASSEV'
    # 输出目录根路径
    SURONG_OUT_PATH = os.getenv('SURONG_OUT_PATH', os.path.abspath('../code'))

class DevelopmentCOnfig(BaseConfig):
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(BaseConfig):
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(BaseConfig):
    # 数据库配置,不知为何会有getenv得到None的情况，所以用OR写在后面
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')  or 'mysql+pymysql://root:root123@127.0.0.1:3306/surong'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'development':DevelopmentCOnfig,
    'production': ProductionConfig,
    'testing' : TestingConfig
}

