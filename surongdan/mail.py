import flask_mail
from flask import Flask, current_app
from threading import Thread

app = Flask(__name__)
# SMTP服务器地址
app.config['MAIL_SERVER'] = 'smtp.163.com'
# SMTP服务器端口，一般为465
app.config['MAIL_PORT'] = 465
# 是否启用SSL加密
app.config['MAIL_USE_SSL'] = True
# 是否启用TLS加密
app.config['MAIL_USE_TLS'] = False
# 登入的邮箱，例如2731510961@qq.com，不能使用无法其他服务的邮箱，例如snbckcode@gmail.com不能使用smtp.qq.com
app.config['MAIL_USERNAME'] = 'exten224@163.com'
# 授权码，在设置smtp的时候有
app.config['MAIL_PASSWORD'] = 'WWLXZTCBXMLASSEV'
# 初始化对象
mail_obj = flask_mail.Mail(app)


# 异步发送邮件
def send_async_email(app, msg):
    with app.app_context():
        mail_obj.send(msg)


def send_mail(to, subject, template, **kwargs):
    """
    :param to: 收件人
    :param subject: 标题名
    :param template: 验证码，之后可以把字符串验证码改为页面
    :param kwargs: 页面参数
    :return:
    """
    # 获取原始app实例
    app1 = current_app._get_current_object()
    # 创建邮件对象
    msgobject = flask_mail.Message(
        subject,
        body="示例邮件的内容",
        sender=app.config['MAIL_USERNAME'],
        recipients=[to]
    )
    # 浏览器接受显示内容
    # msgobject.html = render_template('email/' + template + '.html', **kwargs)

    # 终端接受显示内容
    # msgobject.body = render_template('email/' + template + '.html', **kwargs)
    msgobject.body = template

    # send_async_email(app, msg=msgobject)
    # 使用多线程，先响应请求，再进行与smtp的调用
    thr = Thread(target=send_async_email, args=[app1, msgobject])
    thr.start()
    return thr
