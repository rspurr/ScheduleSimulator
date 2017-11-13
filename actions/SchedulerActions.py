
from src.DayDriver import *
from DayActions import *


class SchedulerActions:
    """
        Scheduler class to be a "front-desk" type of operator
    """
    def __init__(self):
        self._log = logger

    def schedule_appt(self, appt):
        """
        Schedules an appointment for the given day if it can

        :param appt: appointment to be scheduled
        :return: nothing

        """

        schedule = Driver.get_schedule_by_day(appt.date)
        appt_timeslot = self.translate_time_to_slot(appt.time)

        if DayActions.check_appt(appt):
            schedule[appt_timeslot] = appt;
        else:
            self._log.error("{} on day {} is filled".format(appt.time, appt.date))


