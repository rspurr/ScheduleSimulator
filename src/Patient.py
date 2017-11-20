
class Patient(object):
    """
    Class to represent a Patient, which has a number, healthy boolean variable,
    and preferences for scheduling date

    :param num: Patient ID Number

    """

    def __init__(self, num):
        self.id = num
        self.health = True
        self.needs_appt = False
        self.appointments = []
        self.name = ""
        self.chance_of_sickness = 0.2


    def switch_health(self):
        self.health = not self.heatlh
        self.needs_appt = not self.health


