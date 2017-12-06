import logging
import random
import sys

from Patient import Patient
from Day import *
from Appointment import *

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
        self.day_cycle = 0
        self.day_cycle_ctr = 0

        for i in range(0, length):
            self.days.append(Day(i))
        self._log.info("Master Schedule initialized!")

        # initialize the patients
        self.patients = self.create_patients(patients)

        self.release_schedule = [[.2,.3,.4,.5,.6],
                                 [.3,.4,.5,.6,.7],
                                 [],
                                 []]

    def advance_day(self):

        # update driver status vals
        self.curr_day += 1
        self.day_cycle_ctr += 1


        if self.curr_day % 6 == 0:
            self.day_cycle_ctr = 0
            self.day_cycle += 1
            print "NEW CYCLE, OPEN UP MORE APPOINTMENTS"

        # update patients
        self.update_patients()

        print "\n>>> Cycle Day: {}".format(self.day_cycle_ctr)

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

    def schedule_appt(self, appt):
        """
        Schedules an appointment for the given day if it can

        :param appt: appointment to be scheduled
        :return: True if can schedule, False if not

        """
        schedule = driver.get_schedule_by_day(appt.date)
        appt_start = appt.time
        duration = appt.duration / 15
        appt_end = appt_start + duration

        if self.check_appt(appt):
            self._log.info("Scheduling appt for for patient {} on day {} at time {} for {} mins".format(appt.patient.id, appt.date, appt.time, appt.duration))
            for i in range(appt_start, appt_end):
                schedule[i].time = i
                schedule[i] = appt
                schedule[i].open = False
            appt.patient.appointments.append(appt)
            return True
        else:
            self._log.error("Unable to schedule, t{} on day {} is filled".format(appt.time, appt.date))

            return False

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
        if appt_end > len(schedule):
            return False

        for i in range(appt_start, appt_end):
            if schedule[i].open is False:
                avail = False

        return avail

    def get_patients_info(self):
        for patient in self.patients:
            print "ID: {} -- Healthy: {} --- Days Until Appt: {} ".format(patient.id, patient.health, (patient.appointments[0].date - self.curr_day) if len(patient.appointments) > 0 else 0)

    def update_patients(self):
        """
        Updates a Patient's time until appt as well as health
        :return:
        """
        for patient in self.patients:
            if len(patient.appointments) > 0:
                patient.appointments[0].days_since_request += 1
            # flip health if random chance of sickness is satisfied
            if patient.health:
                patient.switch_health() if determine_health(patient.chance_of_sickness) else patient.health
                if not patient.health:
                    scheduled = False
                    for i in range(0, patient.sched_pref):
                        appt_to_sched = Appointment(patient=patient, date=(self.curr_day+i), time=random.randint(0,31),
                                                    duration=(15*random.randint(1,4)), scheduled_on=self.curr_day)
                        if self.check_appt(appt_to_sched):
                            self.schedule_appt(appt_to_sched)
                            scheduled = True
                    if not scheduled:
                        self._log.info("Failed to schedule appointment {} for patient {}".format(appt_to_sched, patient.id))

    def get_first_avail(self):
        # go through days remaining in simulation
        for day in self.days[self.curr_day:]:
            # go through time slots for that day
            for slot in day.times:
                #if slot is available, return day and slot
                if day.schedule[slot] is not None:
                    return day, slot
                else:
                    return None, None

    def create_patients(self, num):
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
                # new_patient.health = determine_health(new_patient.chance_of_sickness)
                # if not healthy, start them off with a scheduled appt
                if not new_patient.health:
                    print "Scheduling appointment for patient {}".format(new_patient.id)
                    new_patient.appointments.append(
                        Appointment(patient=new_patient, date=(self.curr_day + new_patient.sched_pref),
                                    time=random.randint(0, 31), duration=15*random.randint(0,4),
                                    scheduled_on=self.curr_day))
                # add to list
                patients.append(new_patient)

        return patients


# helper functions


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
                else:
                    print "Couldn't Schedule"


if __name__ == "__main__":

    driver = Driver(length=180, patients=100)
    patients = driver.patients

    print Day.schedule_to_string(driver.days[driver.curr_day])

    '''Test scheduling in a blocked timeslot'''
    # new_patient = Patient(101)
    # new_patient.appointments.append(Appointment(new_patient, 0, 8, 15, scheduled_on=curr_day))
    #
    # assert driver.check_appt(new_patient.appointments[0]) is False

    '''Test scheduling in an open timeslot'''
    # new_patient_2 = Patient(102)
    # new_patient_2.appointments.append(Appointment(new_patient_2, 0, 3, 15, scheduled_on=curr_day))
    #
    # assert driver.check_appt(new_patient_2.appointments[0]) is True
    # driver.schedule_appt(new_patient_2.appointments[0])

    # schedule should now have changed timeslot #3 to be unavailable
    # print Day.schedule_to_string(driver.days[curr_day])

    ''' Tests scheduling for multiple patients '''
    #schedule_for_all(driver, patients)

    ''' Tests conflicting scheduling'''
    #test_conflicts(driver, patients)

    #driver.get_patients_info()

    for i in range(0,5):
        driver.advance_day()

        #driver.get_patients_info()

        print Day.schedule_to_string(driver.days[driver.curr_day])
