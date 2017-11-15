import logging
import random
import sys

from Patient import Patient
from Day import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#log_handler = logging.FileHandler("sim.log")
log_stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s >>> %(message)s')
log_stream_handler.setFormatter(formatter)
#logger.addHandler(log_handler)
logger.addHandler(log_stream_handler)


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
        self._log.info("Schedule initialized!")

    def update_curr_schedule(self, new_schedule, day_num):
        """
        Updates the current_day's schedule

        :param new_schedule: the new schedule for the day
        :param day_num: the day to update the schedule on
        :return: the new schedule for the day

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

    def schedule_appt(self, appt):
        """
        Schedules an appointment for the given day if it can

        :param appt: appointment to be scheduled
        :return: nothing

        """
        self._log.info("Scheduling appt for {} on day {}".format(appt.time, appt.date))
        schedule = driver.get_schedule_by_day(appt.date)
        appt_timeslot = appt.time #translate_time_to_slot(appt.time)

        if self.check_appt(appt):
            schedule[appt_timeslot] = appt;
        else:
            self._log.error("{} on day {} is filled".format(appt.time, appt.date))

    def check_appt(self, appt):
        """
        Checks if the appointment can be scheduled that day

        :param appt: appointment we want to schedule
        :return: True if it can schedule, False if not

        """

        appt_timeslot = appt.time #fr_desk.translate_time_to_slot(appt.time)

        schedule = self.get_schedule_by_day(appt.date)

        if schedule[appt.time] is None:
            return True
        else:
            return False

    def schedule_to_string(self, schedule):
        ret = "Time:\t|\t#\n"
        ret += "-"*50
        ret += "\n"
        for key,val in schedule.iteritems():
            if val is not None:
                ret += "{}    |   {}\n".format(translate_slot_to_time(key), val.patient.name)
            else:
                ret += "{}    |   {}\n".format(translate_slot_to_time(key), "*****************")

        return ret


def create_patients(num):
    """
    Creates n amount of patients
    :param int num: number of patients to create
    :return: list of Patient objects
    """

    patients = []

    with open("names", "r+") as f:
        for i in range(num):
            # self._log.debug("Creating patient #{}".format(i))
            patient = Patient(i)
            patient.name = f.readline().strip("\n")
            patient.appointments.append(Appointment(patient, 1, random.randint(0, 95), 15, 1))
            patients.append(patient)

    return patients


if __name__ == "__main__":

    driver = Driver(50)
    patients = create_patients(50)
    curr_day = driver.days[1]
    for patient in patients:
        logger.debug("Checking schedule for today at {}".format(patient.appointments[0].time))
        if driver.check_appt(patient.appointments[0]):
            logger.debug("Scheduling for {}!".format(patient.id))
            driver.schedule_appt(patient.appointments[0])
            curr_day.get_appt(patient.appointments[0].time).patient = patient

    logger.info(driver.schedule_to_string(driver.get_schedule_by_day(1)))

