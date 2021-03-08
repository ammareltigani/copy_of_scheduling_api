from db import db

class UserModel(db.Model):
    # calling the table in the db
    __tablename__ = 'users'

    # setting up the columns for each user in the db
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    full_name = db.Column(db.String(80))
    is_employee = db.Column(db.Boolean)


    def __init__(self, username: str, password: str, full_name: str, is_employee=False):
        # object's filed must match the class's global variable
        self.username = username
        self.password = password
        self.full_name = full_name
        self.is_employee = is_employee


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def json(self):
        return{
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            "is_employee": self.is_employee,
        }


    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
