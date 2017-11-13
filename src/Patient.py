
class Patient:
    """
        Class to represent a Patient, which has a number, healthy boolean variable, and preferences for scheduling date
        :param num: patient ID number
    """

    def __init__(self, num):
        self.id = num
        self.health = True
        self.scheduling_preferences = []
