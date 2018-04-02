import random
from metrics.BasicMetrics import PatientMetrics

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

        self.sched_pref = random.randint(0, 28)
        self.appointments = []

        self.days_until_appt = 0
        self.total_appts = 0
        self.appts_attended = 0

    def switch_health(self):
        '''if self.health is True:
            self.health = False
        self.needs_appt = not self.needs_appt'''

        self.health = False

        '''if self.health is True and len(self.appointments) is not 0:
            self._log.debug("Patient {} returned to healthy pool before appt!")
            for appt in self.appointments:
                print appt'''


