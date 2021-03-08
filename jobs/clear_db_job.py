if __name__ == '__main__':
    from models.appointment import AppointmentModel
    AppointmentModel.delete_past_appointments()