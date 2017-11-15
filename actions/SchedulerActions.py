import logging

from src.DayDriver import *
from DayActions import *

class SchedulerActions:
    """
        Scheduler class to be a "front-desk" type of operator
    """

    def __init__(self, driver):
        self.driver = driver
        self._log = logger


