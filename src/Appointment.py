import datetime
from DayDriver import Driver


class Appointment(object):
    """
    Each slot in the Day's schedule

    :param patient: the patient who scheduled it
    :param time: the time it was scheduled for
    :param duration: the length of the visit

    """

    def __init__(self, patient, date, time, duration):

        self.patient = patient
        self.date = date
        self.time = time
        self.scheduled_time = Driver.curr_day
        self.days_since_request = 0
        self.duration = duration


    # add func to translate date into day_num