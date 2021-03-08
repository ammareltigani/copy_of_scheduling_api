from db import db
from datetime import date
from models.user import UserModel

class AppointmentModel(db.Model):

    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    timeslot = db.Column(db.Integer)

    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    customer = db.relationship('UserModel', foreign_keys=[customer_id])
    employee = db.relationship('UserModel', foreign_keys=[employee_id])


    # whenever customer_id is None, the slot has not been booked by a customer
    def __init__(self, customer_id: int, employee_id: int, date: date, timeslot: int):
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.date = date
        self.timeslot = timeslot


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


    def employee(self):
        return UserModel.find_by_id(self.employee_id)


    def customer(self):
        #assert (self.customer_id), "Cannot get a customer if customer_id is None"
        if self.customer_id:
            return UserModel.find_by_id(self.customer_id)
        return None


    def format_time(self):
        #assert (8 < self.timeslot < 21), "Timeslot must be an int between 8 and 21"
        if self.timeslot == 12:
            return '12:00 PM'
        if self.timeslot > 12:
            return f'{self.timeslot - 12}: 00 PM'
        return f'{self.timeslot}:00 AM'

    def format_customer(self):
        cust = self.customer()
        if cust:
            return cust.json()
        return None

    def serialize_date(self):
        return "{}-{}-{}".format(self.date.year, self.date.month, self.date.day)


    def json(self):
        return {
            'id':self.id,
            'customer': self.format_customer(),
            'employee': self.employee().json(),
            'date': self.serialize_date(),
            'time': self.format_time()
        }


    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user(cls, _id: int, is_employee: bool):
        if is_employee:
            return cls.query.filter_by(employee_id=_id).all()
        return cls.query.filter_by(customer_id=_id).all()

    @classmethod
    def find_by_dateTime(cls, date: date, timeslot: int):
        assert (8 < timeslot < 21), "Time must be an int between 9 and 20."
        return cls.query.filter_by(timeslot=timeslot, date=date).all()

    @classmethod
    def find_by_dateTime_and_user(cls, date: date, timeslot: int, _id: int, is_employee: bool):
        if is_employee:
            return cls.query.filter_by(date=date, timeslot=timeslot, employee_id=_id).first()
        return cls.query.filter_by(date=date, timeslot=timeslot, customer_id=_id).first()

    @classmethod
    def delete_past_appointments(cls):
        cls.query.filter(cls.date < date.today()).delete()
        db.session.commit()

    @classmethod
    def get_all_appointments(cls):
        return cls.query.all()
