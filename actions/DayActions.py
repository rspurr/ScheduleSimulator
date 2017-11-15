
from src.DayDriver import *
from src.Day import *

import logging


class DayActions:
    """
        Methods that help for the Day class
    """
    def __init__(self):
        self._log = logging.getLogger(__name__)

    # helper functions

    def translate_slot_to_time(self, time):
        """
        Translates a standard time i.e. "6:15" and turns it into a timeslot we can use for indexing

        :param time: time we want to convert
        :return: int index the index of the timeslot in the schedule

        """

        hour = time % 24
        mins = (time - (time % 24))*15
        # hour * 4 indexes into the 4 entries for that hour,
        # then minute %15 will index into the appropriate slot in that hour


        return "{}:{}".format(hour, mins)