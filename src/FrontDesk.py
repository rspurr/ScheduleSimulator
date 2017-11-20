import logging
import random
import sys

from Patient import Patient
from Day import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s >>> %(message)s')
log_stream_handler.setFormatter(formatter)
logger.addHandler(log_stream_handler)

#log_handler = logging.FileHandler("sim.log")
#logger.addHandler(log_handler)


class Driver:
    """
        Initializes the schedule and begins simulation of scheduling
    """

    def __init__(self, length, patients):
        self._log = logger

        # create list of days , each with their own schedule
        self.curr_day = 0
        self.days = []
        for i in range(0, length):
            self.days.append(Day(i))
        self._log.info("Schedule initialized!")

        # initialize the patients
        self.patients = create_patients(patients)

    def advance_day(self):

        # update driver status vals
        self.curr_day += 1

        # update patients
        self.update_patients()

    def update_schedule(self, new_schedule, day_num):
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

    def schedule_to_string(self, schedule):
        ret = "\nTime:\t|\tPatient\n"
        ret += "-"*50
        ret += "\n"
        for key,val in schedule.iteritems():
            if val is not None:
                ret += "{}    |   {}\n".format(translate_slot_to_time(key), val.patient.name)
            else:
                ret += "{}    |   {}\n".format(translate_slot_to_time(key), "*****************")

        return ret

    def schedule_appt(self, appt):
        """
        Schedules an appointment for the given day if it can

        :param appt: appointment to be scheduled
        :return: nothing

        """
        schedule = driver.get_schedule_by_day(appt.date)
        appt_start = appt.time
        duration = appt.duration / 15
        appt_end = appt_start + duration

        if self.check_appt(appt):
            self._log.info("Scheduling appt for day {} at time {} for {} mins".format(appt.date, appt.time, appt.duration))
            for i in range(appt_start, appt_end):
                schedule[i] = appt
        else:
            self._log.error("Unable to schedule, t{} on day {} is filled".format(appt.time, appt.date))

    def check_appt(self, appt):
        """
        Checks if the appointment can be scheduled that day

        :param appt: appointment we want to schedule
        :return: True if it can schedule, False if not

        """

        appt_start = appt.time
        duration = appt.duration / 15
        appt_end = appt_start + duration

        schedule = self.get_schedule_by_day(appt.date)
        avail = True
        for i in range(appt_start, appt_end):
            if schedule[i] is not None:
                avail = False

        return avail

    def get_patients_info(self):
        for patient in self.patients:
            print "ID: {} -- Healthy: {} --- Days Until Appt: {} ".format(patient.id, patient.health, patient.appointments[0].date - curr_day if \
            len(patient.appointments) > 0 else None)

    def update_patients(self):
        for patient in self.patients:
            if len(patient.appointments) > 0:
                patient.appointments[0].days_since_request += 1
            # flip health if random chance of sickness is satisfied
            if patient.health:
                patient.switch_health() if determine_health(patient.chance_of_sickness) else patient.health

    def get_first_avail(self):
        # go through days remaining in simulation
        for day in self.days[self.curr_day:]:
            # go through time slots for that day
            for slot in day.times:
                #if slot is available, return day and slot
                if day.schedule[slot] is not None:
                    return day, slot
                else:
                    pass


# helper functions
def create_patients(num):
    """
    Creates n amount of patients
    :param int num: number of patients to create
    """

    patients = []

    with open("names", "r+") as f:
        for i in range(num):
            new_patient = Patient(i)
            new_patient.name = f.readline().strip("\n")

            # assign a random health value
            new_patient.health = determine_health(new_patient.chance_of_sickness)
            # if not healthy, start them off with a scheduled appt
            if not new_patient.health:
                new_patient.appointments.append(Appointment(new_patient, random.randint(0,49), random.randint(0, 31), 15, 0))
            # add to list
            patients.append(new_patient)

    return patients


def determine_health(prob):
    rand = random.random()
    if rand < prob:
        return True
    else:
        return False


def test_conflicts(driver, patients):
    ''' Schedule first patient's appt '''
    patients[0].appointments.append(Appointment(patient=patients[0], date=1, time=0, duration=30, scheduled_on=1))
    driver.schedule_appt(patients[0].appointments[0])

    ''' Schedule second patient's appt '''
    patients[1].appointments.append(Appointment(patient=patients[1], date=1, time=1, duration=30, scheduled_on=1))
    driver.schedule_appt(patients[1].appointments[0])


def schedule_for_all(driver, patients):
    """
    Schedules an appt for all patients that require one
    :param driver:
    :param patients:
    :return:
    """

    for patient in patients:
        if patient.needs_appt:
            if len(patient.appointments) > 0:
                logger.debug("Checking schedule for day {} at {}".format(patient.appointments[0].date, patient.appointments[0].time))
                if driver.check_appt(patient.appointments[0]):
                    logger.debug("Scheduling for {}!".format(patient.id))
                    driver.schedule_appt(patient.appointments[0])


if __name__ == "__main__":

    driver = Driver(50, 50)
    patients = driver.patients
    curr_day = driver.curr_day

    ''' Tests scheduling for multiple patients '''
    schedule_for_all(driver, patients)

    ''' Tests conflicting scheduling'''
    #test_conflicts(driver, patients)

    driver.get_patients_info()

    driver.advance_day()

    driver.get_patients_info()
