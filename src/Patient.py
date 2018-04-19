import random


class Patient(object):
    """
    Class to represent a Patient, which has a number, healthy boolean variable,
    and preferences for scheduling date

    :param num: Patient ID Number

    """

    def __init__(self, num):
        self.id = num
        self.name = ""

        self.health = True
        self.needs_appt = False

        self.sched_pref = random.randint(0, 28)
        self.appointments = []

        self.days_until_appt = 0
        self.total_appts = 0
        self.appts_attended = 0

        self.state = "healthy"

    def switch_health(self):
        if self.health is True:
            self.health = False
        self.needs_appt = True

        self.state = "sick_needs_appt"

    def __str__(self):
        return "{} : {}".format(self.id, self.state)

class PatientStateMachine:

    def __init__(self):
        self.patients = []
        self.states = ["no_appt", "sick_need_appt", "sick_w_appt", "healthy", "healthy_w_appt"]
