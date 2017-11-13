from Appointment import Appointment


class Day:
    """
        Day : Has a list of times and a map of times -> appointments
        :param num: the number of the day; for indexing purposes
    """
    def __init__(self, num):
        self.day_num = num
        self.times = []
        self.schedule = {}

        # have a slot for every 15 minutes in the day
        for i in range(0, 24*4):
            self.schedule[i] = None




    # event handling

    #



