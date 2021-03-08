from datetime import date
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity
)
from models.appointment import AppointmentModel


def deserialize_date(d): # String --> datetime.date
    #if not validate_date(d):
    #    return some error

    d_list = d.split("-")
    d_list = [int(x) for x in d_list]
    return date(*d_list)

def validate_date(d):
    # TODO: add verifier to make time format is correct
    pass

# TODO: implement format validator
def validate_availabilities(data):
    return True


class AppointmentList(Resource):
    @jwt_required
    def get(self):
        identity = get_jwt_identity()
        user_id = identity['id']
        claims = get_jwt_claims()
        is_employee = claims['is_employee']
        appointments = AppointmentModel.find_by_user(user_id, is_employee)
        return {'appointments': [apt.json() for apt in appointments]}, 200


class Appointment(Resource):
    @jwt_required
    def get(self, date, timeslot):
        appointments = AppointmentModel.find_by_dateTime(deserialize_date(date), timeslot)
        if appointments:
            return {'appointments': [appt.json() for appt in appointments]}, 200
        return {'message': "No appointments found for that date and time."}, 404

    @jwt_required
    def put(self, date, timeslot):
        parser = reqparse.RequestParser()
        parser.add_argument('employee_id',
            type=int,
            required=True,
            help="This field cannot be left blank!"
        )
        data = parser.parse_args()
        appointment = AppointmentModel.find_by_dateTime_and_user(deserialize_date(date), timeslot, data['employee_id'], True)
        if not appointment:
            return {'message': 'Appointment does not exist'}, 404
        if appointment.customer_id:
            return {'message': 'This appointment is already booked by another customer.'}, 409

        identity = get_jwt_identity()
        appointment.customer_id = identity['id']
        appointment.save_to_db()
        return {'message': 'Successfully booked appointment'}, 201


    @jwt_required
    def delete(self, date, timeslot):
        identity = get_jwt_identity()
        user_id = identity['id']
        claims = get_jwt_claims()
        is_employee = claims['is_employee']

        appointment = None
        if is_employee:
            appointment = AppointmentModel.find_by_dateTime_and_user(deserialize_date(date), timeslot, user_id, True)
        else:
            appointment = AppointmentModel.find_by_dateTime_and_user(deserialize_date(date), timeslot, user_id, False)

        if appointment:
            if is_employee:
                appointment.delete_from_db()
            else:
                appointment.customer_id = None
                appointment.save_to_db()
            return {'message': 'Successfully cancelled appointment.'}, 200
        return {'message': 'Appointment does not exist.'}, 404



class Schedule(Resource):
    @jwt_required
    def get(self): 
        return {'schedule': [appt.json() for appt in AppointmentModel.get_all_appointments()]}, 200

    @jwt_required
    def post(self): 
        # we don't want to let customers create unscheduled appointments, since
        # these signal an availability (open slot) of a particular employee
        claims = get_jwt_claims()
        if not claims['is_employee']:
            return {'message': 'Only employee can create unscheduled appointments'}, 403

        # we need the identity of the employee to show customers which workers
        # are free during particular timeslots
        jwt_info = get_jwt_identity()
        employee_id = jwt_info['id']

        print(employee_id)

        data = request.json
        if not validate_availabilities(data):
            return {'message': 'Cannot create appointments because request body\
            is misformatted'}

        # iterate over all date and timeslots provided by said customer and create
        # all the unscheduled appointments
        flag = False
        for sch in data['schedule']:
            old_appt = AppointmentModel.find_by_dateTime_and_user(sch['date'], sch['timeslot'], employee_id, True)
            if old_appt:
                flag = True
                continue
            appt = AppointmentModel(None, employee_id, deserialize_date(sch['date']), sch['timeslot'])                
            try:
                appt.save_to_db()
            except:
                return {'message': 'Something went wrong with saving an appointment.'}, 500

        if flag:
            return {'message': 'Some unscheduled appointments were not created because employee is already booked at such date and time.'}, 201
        return {'message': 'Successfully created all unscheduled appointments'}, 201 
