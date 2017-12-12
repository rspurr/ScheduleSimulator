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
        self.chance_of_sickness = 0.2

        self.sched_pref = random.randint(0, 5)
        self.appointments = []

    def switch_health(self):
        self.health = not self.health
        self.needs_appt = not self.needs_appt

        if self.health is True and len(self.appointments) is not 0:
            print("Patient LOST!")


