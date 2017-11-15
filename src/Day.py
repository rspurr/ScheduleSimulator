from Appointment import Appointment


class Day(object):
    """
    Class to represent a Day in a Schedule

    :param num: the number of the day; for indexing purposes

    """

    def __init__(self, num):

        self.day_num = num
        self.times = []
        self.schedule = {}

        # have a slot for every 15 minutes in the day
        for i in range(0, 24*4):
            self.schedule[i] = None

    def get_appt(self, time):
        return self.schedule[time]

def translate_slot_to_time(time):
    """
    Translates a standard time i.e. "6:15" and turns it into a timeslot we can use for indexing

    :param time: time we want to convert
    :return: int index the index of the timeslot in the schedule

    """

    mins = 0
    hours = 0
    for i in range(time/4):
        for i in range(0, 4):
            mins += 15
            if mins >= 60:
                hours+=1
                mins = 0

    mins = time*15 - (hours*4*15)
    if mins == 0:
        return "{}:00".format(hours)
    else:
        return "{}:{}".format(hours, mins)

    # event handling

    #



