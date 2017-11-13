
from DayDriver import Driver, logger
from Day import *


class DayActions:

    def __init__(self):
        self._log = logger

    # helper functions

    def check_appt(self, appt):
        """
        Checks if the appointment can be scheduled that day
        :param appt:
        :return:
        """
        appt_timeslot = self.translate_time_to_slot(appt.time)
        schedule = Driver.get_schedule_by_day(appt.date)

        if schedule[appt_timeslot] is not None:
            return True
        else:
            return False

    def translate_time_to_slot(self, time):
        hour, minute = time.split(":")

        # hour * 4 indexes into the 4 entries for that hour,
        # then minute %15 will index into the appropriate slot in that hour
        index = hour*4 + minute%15

        return index