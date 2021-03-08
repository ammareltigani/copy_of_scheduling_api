# [Project Salon] Backend Design ☕
This will serve as notes  for planning and further iteration of the API we will be developing to support the salon appointment scheduling web app

Minimum requirements:  


    -Allow employees and customer to register
    -Allow employees and customers to login
    -Allow employee to enter schedule
    -Allow employees and users to view their schedule (showing booked appointments)
    -Allow customers to make reservation on a timeslot that has available employees
    -Allow customers to choose which employee they wish to make an appointment with
    -Allow users to cancel their own appointment
    -Delete past appointments from db (automatically)


## Challenges:
[x] How to map dateTime string to a unique id for each time slot
[x] Want to make each user delete their own slot only
[x] Creating relations between Employees and appointments
[x] Creating relation between Customers and appointments


## Remaining steps:
[x] Forbid customers from creating unscheduled appiontments (currently ‘claims’ syntax not working)
[x] Write cronjob that automatically deletes past appointments
[x] Forbid employee from creating two unscheduled appointments in the same timeslot
[x] Removed unused classmethods in models/appointment.py
[ ] Implement custom format-validating functions for date and availabilities
[ ] Make it so that customers only have to send username of employees they would like book an appointment with. Not id.
[ ] Migrate blacklists to a database table instead of in-memory python set
[ ] Provide proper API documentation
[ ] Implement better error checking and handling
[ ] Make secret_key and employee_code protected os environment variables
[ ] Create an admin or superuser for the owner of the app
[ ] Write more thorough Postman tests
[ ] Deploy to Heroku or ElasticBeastalk
[ ] Deploy to AWS EC2 instance long-term
[ ] Update README.md


## Relationships:
    - Each Employee and Customer can have several appointments
    - Each appointment has one employee and one user
    - Timeslots are represented in each appointment as date and time columns


## Design Choices:
    - An appointment without a customer means an availability


## Models
    class AppointmentModel:
      int id,
      datetime.date date, "MM/DD/YYYY"
      int timeslot, //between 8 and 21
      int employee_id, //default: None
      int customer_id,
      
    class UserModel:
      int id,
      string username,
      string password,
      string full_name,
      string is_employee



## Resources


    **note: [Auth: ...] specifies the highest permission required to call endpoint
    
    Schedule
    ------------------
        // list of all appointments in db (booked as well as open)
        GET /schedule [Auth: Customer]
    
        // creates unbooked appointments that represent availability of employees
        POST /schedule [Auth: Employee] 
            Body {
                  "schedule": [
                               {"timeslot": 10,
                                "date": "2001-05-21"},
                               {"timeslot": 11,
                                "date": "2001-05-22"},                                     
                              ]
                  }


    AppointmentList
    ---------------------
        // list of booked appointments for the user (employee or customer)
        GET /appointments [Auth: Customer]
    
    Appointment
    ---------------------
        //gets all appointments in a given timeslot
        GET /appointment/<string:date>/<int:slot> [Auth: Customer]
    
        // assigns a customer to an already existing appointment essentially booking it
        // (only customers can book) use reverse claims
        PUT /appointment/<string:date>/<int:slot> [Auth: Customer]
        Body {
              "employee_username": "jamesB54"
            }
    
        // deletes a customer or employee's appointment if it is their own
        // (checks in db if one appt in that timeslot exists in their name)
        DELETE /appointment/<string:date>/<int:slot> [Auth: Customer]
    


    User
    -------------------
        // registers employees or customers for the first time. If employee, must provide secret code
        POST /register
        Body {
          "usename": username,
          "password": password,
          "full_name": full_name,
          [OPTIONAL] "employee_code": code
        }
    
        // logs in user by returning a fresh JWT
        POST /login
        Body {
          "username": username,
          "password": password
        }
    
        // logs out user by destroying JWT in header
        POST /logout  [Auth: Customer]



## Front end sample (??)
|       | Monday        | Tuesday                                 | Wednesday |
| ----- | ------------- | --------------------------------------- | --------- |
| 9 am  | Rachel:  None | Rachel:  Hamza, Geremy<br>Richard: None | …         |
| 10 am | Rachel:  John | …                                       | …         |
