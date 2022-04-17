from surongdan.extensions import db 

class user_table(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable = False)
    user_email = db.Column(db.String(120), nullable= False)
    user_pwd = db.Column(db.String(120), nullable=False)
    user_status = db.Column(db.Boolean, nullable=False)
    def __repr__(self):
        return '<user %d %s %s>' % (self.user_id, self.user_name, self.user_email)


