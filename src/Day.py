from Appointment import translate_slot_to_time


class Day(object):
    """
    Class to represent a Day in a Schedule

    :param num: the number of the day; for indexing purposes

    """

    def __init__(self, num):

        self.day_num = num
        self.schedule = []
        self.percent_avail = 0.2
        # have a slot for every 15 minutes in the day
        # schedule N% of appts as open for the given day
        for i in range(0, int(8*self.percent_avail*4)):
            self.schedule.append(Timeslot(i, open=True))

        # initialize rest of timeslots but block them from being available for scheduling
        for i in range(int(8*self.percent_avail*4), 8*4):
            self.schedule.append(Timeslot(i, open=False))

    def get_appt(self, time):
        return self.schedule[time].appt

    def schedule_to_string(self):
        ret = ">>> Day: {}\n".format(self.day_num)
        for i in self.schedule:
            ret += "{}\n".format(str(i))
        return ret

    # event handling

    #


class Timeslot(object):
    """
    Timeslot object #TODO doc this
    """
    def __init__(self, time, open):
        self.time = time
        self.appt = None
        self.open = open

    def __str__(self):
        if self.appt is None or self.open:
            slot = "Time: {}     |     Avail: {}".format(translate_slot_to_time(self.time), self.open)
        else:
            slot = "Time: {}     |     Patient: {}".format(translate_slot_to_time(self.time), self.appt.patient.id)
        return slot

