import logging, random, sys, math
import numpy
import pandas as pd

from Patient import Patient
from Day import *
from Appointment import *
from metrics.BasicMetrics import BasicMetrics, PatientMetrics, ApptMetrics
import config as conf

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# log_stream_handler = logging.StreamHandler(sys.stdout)

# logger.addHandler(log_stream_handler)

logging.basicConfig(format='[SIMLOG] %(levelname)s - %(message)s',
                    filemode='w',
                    filename='sim.log',
                    )


class FrontDesk:
    """
        Initializes the schedule and begins simulation of scheduling
    """

    def __init__(self, config):
        self._log = logger

        # create list of days , each with their own schedule
        self.curr_day = 0
        self.days = []
        self.day_cycle = 0
        self.day_cycle_ctr = 0

        self.conf = config[0]

        # create days with their corresponding cycle day (day in the week)
        for i in range(0, self.conf['scheduling_horizon'] + 1):
            self.day_cycle_ctr += 1
            if self.day_cycle_ctr % 7 == 0:
                self.day_cycle_ctr = 1
            self.days.append(Day(i, self.day_cycle_ctr))
        # reset cycle day counter
        self.day_cycle_ctr = 0

        # initialize the patients
        self.patients = self.create_patients(num=self.conf['num_patients'])

        # separate healthy and sick patients
        self.healthy = []
        self.sick = []
        # keep track of scheduled appointments for metrics
        self.scheduled_appts = []

        self.release_schedule = config[1]

        ''' calculate probabilities of a call from a sick patient depending
            on day of week '''

        calls_per_day = [191.4, 166.25, 120, 126.5, 98, 65.6]
        sum_calls = sum(calls_per_day)
        self.chance_of_call = list(map(lambda x: x / sum_calls, calls_per_day))

        self.metrics = BasicMetrics()
        self.tracker = PatientMetrics()
        self.appt_tracker = ApptMetrics()

    ''' Simulation Code '''

    def advance_day(self):
        '''
        Simulates the advancement of a day in the schedule.  Goes through and opens up slots
        after each day for the specified range of days.  Also updates cycle and day information vars.
        :return:
        '''

        self._log.info("Day: {}".format(self.curr_day))

        self.sim_appts()

        # release slots in specified day range
        for day in [1, 3, 7, 14, 28]:
            release_day = self.days[self.curr_day + day]

            first_closed = release_day.get_first_closed_slot()
            fc_index = release_day.schedule.index(first_closed)
            for i in range(fc_index, int(fc_index + (self.release_schedule[day]) * 32) - 1):
                if release_day.day_num < len(self.days) - 1:
                    self._log.info("Opening slot : Day {} {}".format(release_day.day_num, release_day.schedule[i]))
                    release_day.schedule[i].open = True

        # update fd status vals
        self.curr_day += 1
        self.day_cycle_ctr += 1

        if self.curr_day % 7 == 0:
            self.day_cycle_ctr = 1
            self.day_cycle += 1
            print "\n>>> Week (cycle) {} has finished.".format(self.day_cycle - 1)

        # update patients
        self.update_patients()

    def sim_appts(self):

        for slot in self.days[self.curr_day].schedule:
            # if patient is still sick assume they attend
            if slot.appt is not None:
                if slot.appt.patient.health is False:
                    slot.appt.attended = True
                    slot.appt.patient.appts_attended += 1
                    slot.appt.patient.health = True
                    self.metrics.appts_attended += 1

                    # TODO: make change pool method

                    if slot.appt.patient in self.sick:
                        self.sick.remove(slot.appt.patient)
                    if slot.appt.patient not in self.healthy:
                        self.healthy.append(slot.appt.patient)
                else:
                    slot.appt.attended = False

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
        schedule = fd.get_schedule_by_day(appt.date)
        appt_start = appt.time
        duration = appt.duration / 15
        appt_end = appt_start + duration

        if self.check_appt(appt):
            self._log.info(
                "Scheduling appt for for patient {} on day {} at {} for {} mins".format(appt.patient.id, appt.date,
                                                                                        translate_slot_to_time(
                                                                                            appt.time), appt.duration))
            for i in range(appt_start, appt_end):
                schedule[i].time = i
                schedule[i].appt = appt
                schedule[i].open = False
            # update patient records
            appt.patient.appointments.append(appt)
            appt.patient.days_until_appt = appt.date - self.curr_day
            appt.patient.total_appts += 1
            self.scheduled_appts.append(appt)
            self.metrics.appts_scheduled += 1
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

    def update_patients(self):
        """
        Updates a Patient's time until appt as well as health
        :return:
        """

        for patient in self.patients:
            if len(patient.appointments) > 0:
                for appt in patient.appointments:
                    appt.days_since_request += 1

            # flip health if random chance of sickness is satisfied
            # day in cycle determines chance of the person calling
            if determine_health(self.chance_of_call[self.days[self.curr_day].day_in_cycle - 1]):
                patient.switch_health()

            if patient.health is False:
                self.metrics.daily_requests += 1

                if patient not in self.sick:
                    self.sick.append(patient)
                if patient in self.healthy:
                    self.healthy.remove(patient)

                scheduled = False
                appt = None

                # loop through patient's schedule preferences and attempt to satisfy one

                policy = getattr(fd, self.conf['policy'])

                for i in range(0, patient.sched_pref):
                    appt = Appointment(patient=patient,
                                       date=(self.curr_day + i),
                                       time=policy(self.curr_day + i),
                                       # this is where our policy comes into play
                                       duration=(15 * random.randint(1, 4)), scheduled_on=self.curr_day)

                    # schedule the appointment they want if we can
                    if self.check_appt(appt) and scheduled is not True:
                        self.schedule_appt(appt)
                        scheduled = True

                        break

                # patient is lost
                if scheduled is not True:

                    self._log.info("Failed to schedule appt for for patient {}".format(patient.id))

                    if patient in self.sick:
                        self.sick.remove(patient)
                    if patient not in self.healthy:
                        self.healthy.append(patient)
                    self.metrics.appts_not_scheduled += 1

            else:
                if patient in self.sick:
                    self.sick.remove(patient)
                if patient not in self.healthy:
                    self.healthy.append(patient)

    def cancel_appt(self, appt):
        schedule = fd.get_schedule_by_day(appt.date)
        duration = appt.duration / 15
        appt_end = appt.time + duration

        for i in range(appt.time, appt_end):
            schedule[i].appt = None
            schedule[i].open = True

        print "[+] Appt cancelled."

    def prob_utilized(self, appt):
        b_0 = 0.51517
        b_1 = 0.201328
        b_2 = 0.146079
        B_1 = 1.1486
        B_2 = 0.0356
        t = appt.days_since_request

        y = b_0 + math.fsum([b_1 * math.pow(math.e, (-B_1 * t)), b_2 * math.pow(math.e, (-B_2 * t))])

        return y

    '''Scheduling Policies'''

    def get_first_avail(self, day):
        """
        Gets first available slot in the day
        :param day: day to get first avail slot from
        :return: timeslot # of first open
        """
        # go through times in the day
        for slot in self.days[day].schedule:
            # if slot is available, return slot time
            if slot.appt is None and slot.open is True:
                return slot.time
        return -1

    '''Helper Functions'''

    def get_patients_info(self):
        for patient in self.patients:
            print "ID: {} -- Healthy: {} --- Days Until Appt: {} ".format(patient.id, patient.health, (
                patient.appointments[0].date - self.curr_day) if len(patient.appointments) > 0 else 0)

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


def test_conflicts(fd, patients):
    ''' Schedule first patient's appt '''
    patients[0].appointments.append(Appointment(patient=patients[0], date=1, time=0, duration=30, scheduled_on=1))
    fd.schedule_appt(patients[0].appointments[0])

    ''' Schedule second patient's appt '''
    patients[1].appointments.append(Appointment(patient=patients[1], date=1, time=1, duration=30, scheduled_on=1))
    fd.schedule_appt(patients[1].appointments[0])


def schedule_for_all(fd, patients):
    """
    Schedules an appt for all patients that require one
    :param fd:
    :param patients:
    :return:
    """

    for patient in patients:
        if patient.needs_appt:
            if len(patient.appointments) > 0:
                logger.debug("Checking schedule for day {} at {}".format(patient.appointments[0].date,
                                                                         patient.appointments[0].translate_appt_to_time(
                                                                             patient.appointments[0].time)))

                if fd.check_appt(patient.appointments[0]):
                    logger.debug("Scheduling for {}!".format(patient.id))
                    fd.schedule_appt(patient.appointments[0])
                else:
                    print "Couldn't Schedule"


def print_metrics(fd):
    print ("\n>>>>>> DAY {} <<<<<<<\n".format(fd.curr_day))
    print "----- Scheduling Metrics -----"
    print ">>> Scheduled Total: {}\n>>> Failed to Schedule Total: {}".format(fd.metrics.appts_scheduled,
                                                                             fd.metrics.appts_not_scheduled)
    print ">>> Scheduled for Today:\n" \
          ">>> Attended: {}\n>>> Total Calls: {}\n".format(fd.metrics.appts_attended,
                                                           fd.metrics.requests_total)

    print "----- Patient Metrics -----"
    print ">>> Healthy: {}\n>>> Sick: {}".format(len(fd.healthy), len(fd.sick))


def run_simulation(length, sim_num):
    for i in range(0, length):
        # simulate day and display metrics
        fd.advance_day()
        appt_ctr = 0
        for slot in fd.days[fd.curr_day].schedule:
            if slot.appt is not None:
                appt_ctr += 1

        fd.metrics.append_to_df(i)

    fd.tracker.append_to_df(fd.patients)
    fd.appt_tracker.append_to_df(fd.scheduled_appts)

    writer = pd.ExcelWriter("Metrics_Run_{}.xlsx".format(sim_num), engine="openpyxl")
    fd.metrics.metrics_df.to_excel(writer, "Simulation Data")
    fd.tracker.metrics_df.to_excel(writer, "Patient Data")
    fd.appt_tracker.metrics_df.to_excel(writer, "Appointment Data")
    writer.save()


if __name__ == "__main__":

    configs = conf.get_configs()
    for i in range(len(configs)):
        fd = FrontDesk(config=configs[i])
        patients = fd.patients
        print configs[i]
        run_simulation(1, i)
