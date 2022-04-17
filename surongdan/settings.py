import os
from surongdan import app 

# 程序秘钥
SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

# 数据库配置
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False

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

