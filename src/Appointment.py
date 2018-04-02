import datetime
from FrontDesk import Driver


class Appointment(object):
    """
    Each slot in the Day's schedule

    :param patient: the patient who scheduled it
    :param time: the time it was scheduled for
    :param duration: the length of the visit

    """

    def __init__(self, patient, date, time, duration, scheduled_on):

        self.patient = patient
        self.date = date
        self.time = time
        self.scheduled_date = scheduled_on
        self.days_since_request = 0
        self.duration = duration


    def __str__(self):
        return "Day {}     |    Time: {}     |     Patient: {}".format(self.date, translate_slot_to_time(self.time), self.patient.id)


def translate_slot_to_time(time):
    """
    Translates a standard time i.e. "6:15" and turns it into a timeslot we can use for indexing

    :param time: time we want to convert
    :return: int index the index of the timeslot in the schedule

    """

    mins = 0
    hours = 0
    for i in range(time / 4):
        for i in range(0, 4):
            mins += 15
            if mins >= 60:
                hours += 1
                mins = 0

    mins = time * 15 - (hours * 4 * 15)
    if mins == 0:
        return "{}:00".format(hours + 9 if hours + 9 < 13 else ((hours + 9) - 12))
    else:
        return "{}:{}".format(hours + 9 if hours + 9 < 13 else ((hours + 9) - 12), mins)

        # add func to translate date into day_num