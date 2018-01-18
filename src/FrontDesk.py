import logging
import random
import sys
import numpy


from Patient import Patient
from Day import *
from Appointment import *
from metrics.BasicMetrics import BasicMetrics

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s >>> %(message)s')
log_stream_handler.setFormatter(formatter)
#logger.addHandler(log_stream_handler)

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
            self.day_cycle_ctr += 1
            if self.day_cycle_ctr % 7 == 0:
                self.day_cycle_ctr = 1
            self.days.append(Day(i, self.day_cycle_ctr))


        self.day_cycle_ctr = 0

        self._log.info("Master Schedule initialized!")

        # initialize the patients
        self.patients = self.create_patients(patients)

        # separate healthy and sick patients
        self.healthy = self.patients
        self.sick = []
        '''                       1  3   7  14   28 '''
        self.release_schedule = [.2, .2, .2, .2, .2]


        # calculate probabilities of

        calls_per_day = [191.4, 166.25, 120, 126.5, 98, 65.6]
        sum_calls = sum(calls_per_day)

        self.chance_of_call = list(map(lambda x: x/sum_calls, calls_per_day))

        print self.chance_of_call

        self.met = BasicMetrics()

    def advance_day(self):
        self.sim_appts()

        # update driver status vals
        self.curr_day += 1
        self.day_cycle_ctr += 1

        for day in self.days:
            if day.day_num - 1 == self.curr_day:
                first_closed = day.get_first_closed_slot()
                fc_index = day.schedule.index(first_closed)

                for i in range(fc_index, int(fc_index + (self.release_schedule[0])*32)):
                    self._log.info("Opening slot : Day {} {}".format(day.day_num, day.schedule[i]))
                    day.schedule[i].open = True

            elif day.day_num - 3 == self.curr_day:
                first_closed = day.get_first_closed_slot()
                fc_index = day.schedule.index(first_closed)

                for i in range(fc_index, int(fc_index + (self.release_schedule[0]) * 32)):
                    self._log.info("Opening slot : Day {} {}".format(day.day_num, day.schedule[i]))
                    day.schedule[i].open = True

            elif day.day_num - 7 == self.curr_day:
                first_closed = day.get_first_closed_slot()
                fc_index = day.schedule.index(first_closed)

                for i in range(fc_index, int(fc_index + (self.release_schedule[0]) * 32)):
                    self._log.info("Opening slot : Day {} {}".format(day.day_num, day.schedule[i]))
                    day.schedule[i].open = True

            elif day.day_num - 14 == self.curr_day:
                first_closed = day.get_first_closed_slot()
                fc_index = day.schedule.index(first_closed)

                for i in range(fc_index, int(fc_index + (self.release_schedule[0]) * 32)):
                    self._log.info("Opening slot : Day {} {}".format(day.day_num, day.schedule[i]))
                    day.schedule[i].open = True

            elif day.day_num - 28 == self.curr_day:
                first_closed = day.get_first_closed_slot()
                fc_index = day.schedule.index(first_closed)

                for i in range(fc_index, int(fc_index + (self.release_schedule[0]) * 32)):
                    self._log.info("Opening slot : Day {} {}".format(day.day_num, day.schedule[i]))
                    day.schedule[i].open = True


        if self.curr_day % 7 == 0:
            self.day_cycle_ctr = 1
            self.day_cycle += 1
            print "\n>>> Cycle {} has finished.".format(self.day_cycle-1)


        # update patients
        self.update_patients()

    def sim_appts(self):
        patients_attended = []
        patients_not_attended = []

        for slot in self.days[self.curr_day].schedule:
            # if patient is still sick assume they attend
            if slot.appt is not None:
                if slot.appt.patient in self.sick:
                    if slot.appt.patient.id not in patients_attended:
                        patients_attended.append(slot.appt.patient.id)

                    slot.appt.patient.appointments.remove(slot.appt)

                    if slot.appt.patient in self.sick:
                        self.sick.remove(slot.appt.patient)
                    if slot.appt.patient not in self.healthy:
                        self.healthy.append(slot.appt.patient)

        self.met.appts_attended += len(patients_attended)

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
                schedule[i].appt = appt
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
        if appt.time == -1:
            return False
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
            # day in cycle determines chance of the person calling
            if determine_health(self.chance_of_call[self.days[self.curr_day].day_in_cycle-1]):
                patient.switch_health()

            if not patient.health:
                self.met.requests_total += 1

                if patient not in self.sick:
                    self.sick.append(patient)
                if patient in self.healthy:
                    self.healthy.remove(patient)

                scheduled = False
                appt = None

                # loop through patient's schedule preferences and attempt to satisfy one

                for i in range(0, patient.sched_pref):
                    appt = Appointment(patient=patient, date=(self.curr_day+i),
                                       time= self.get_first_avail(self.curr_day+i),
                                        duration=(15*random.randint(1,4)), scheduled_on=self.curr_day)


                    # schedule the appointment they want if we can
                    if self.check_appt(appt) and scheduled is not True:
                        self.schedule_appt(appt)
                        scheduled = True
                        break
                    else:
                        '''print "Failed to schedule appt for for patient {} on day {} at time {} for {} mins".format(
                                appt.patient.id, appt.date, appt.time, appt.duration)'''
                        self._log.info(
                            "Failed to schedule appt for for patient {} on day {} at time {} for {} mins".format(
                                appt.patient.id, appt.date, appt.time, appt.duration))

                # metrics

                if scheduled is True:
                    self.met.appts_scheduled += 1
                else:
                    # lost patient
                    if patient in self.sick:
                        self.sick.remove(patient)
                    if patient not in self.healthy:
                        self.healthy.append(patient)
                    self.met.appts_not_scheduled += 1
            else:
                if patient in self.sick:
                    self.sick.remove(patient)
                if patient not in self.healthy:
                    self.healthy.append(patient)

    def get_first_avail(self, day):
        """
        Gets first available slot in the day
        :param day: day to get first avail slot from
        :return: timeslot # of first open
        """
        # go through times in the day
        for slot in self.days[day].schedule:
            #if slot is available, return day and slot
            if slot.appt is None and slot.open is True:
                return slot.time
        return -1

    def create_patients(self, num):
        """
        Creates n amount of patients
        :param int num: number of patients to create
        """

        patients = []


        for i in range(num):
            new_patient = Patient(i)

            patients.append(new_patient)

        return patients


# helper functions


def determine_health(prob):
    """
    Returns if person gets sick
    :param prob:
    :return:
    """
    rand = random.random()
    if rand <= prob:
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

    for i in range(0, 5):

        driver.advance_day()
        appt_ctr = 0
        for slot in driver.days[driver.curr_day].schedule:
            if slot.appt is not None:
                appt_ctr += 1
        print ("\n>>>>>> DAY {} <<<<<<<\n".format(driver.curr_day))
        print "----- Scheduling Metrics -----"
        print ">>> Scheduled Total: {}\n>>> Failed to Schedule Total: {}".format(driver.met.appts_scheduled, driver.met.appts_not_scheduled)
        print ">>> Scheduled for Today: {}\n" \
              ">>> Attended: {}\n>>> Total Calls: {}\n".format(appt_ctr, driver.met.appts_attended,
                                                                driver.met.requests_total)


        print "----- Patient Metrics -----"
        print ">>> Healthy: {}\n>>> Sick: {}".format(len(driver.healthy), len(driver.sick))


        #driver.get_patients_info()

        # print Day.schedule_to_string(driver.days[driver.curr_day])
