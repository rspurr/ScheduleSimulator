
from src.DayDriver import *
from DayActions import *


class SchedulerActions:

    def __init__(self):
        self._log = logger

    def schedule_appt(self, appt):
        schedule = Driver.get_schedule_by_day(appt.date)
        appt_timeslot = self.translate_time_to_slot(appt.time)

        if DayActions.check_appt(appt):
            schedule[appt_timeslot] = appt;
        else:
            self._log.error("{} on day {} is filled".format(appt.time, appt.date))


