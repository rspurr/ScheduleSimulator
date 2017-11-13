
class Patient:
    """
        Class to represent a Patient, which has a number,
        healthy boolean variable, and preferences for scheduling date
    """

    def __init__(self, num):
        self.num = num
        self.health = True
        self.scheduling_preferences = []
