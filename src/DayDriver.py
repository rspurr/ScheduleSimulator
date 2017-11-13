from Day import Day
from actions.SchedulerActions import *


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.FileHandler("sim.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)


class Driver:
    """
        Initializes the schedule and begins simulation of scheduling
    """
    def __init__(self, length):
        self._log = logger

        # record of states
        self.states = []

        # day list
        self.days = []
        for i in range(0, length):
            self.days.append(Day(i))
        self.curr_day = self.days[0]
        self._log.info("Schedule initialized!")


    def update_curr_schedule(self, new_schedule, day_num):
        """
        Updates the current_day's schedule
        :param new_schedule: the new schedule for the day
        :param day_num: the day to update the schedule on
        :return:
        """
        self.days[day_num].schedule = new_schedule;

        self._log.debug("Updated schedule for day {}".format(self.curr_day.day_num))

        return self.days[self.curr_day.day_num].schedule

    def get_schedule_by_day(self, day_num):
        """
        Gets the schedule of the specified day
        :param day_num: the day to get the schedule for
        :return: the schedule of the day specified
        """
        return self.days[day_num].schedule


if __name__ == "__main__":
    driver = Driver(50)
    print driver.get_schedule_by_day(0)
