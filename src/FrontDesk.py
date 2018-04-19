import logging, random, math
import pandas as pd

from Patient import Patient
from Day import *
from Appointment import *
from metrics.Metrics import BasicMetrics, PatientMetrics, ApptMetrics
import config as conf

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(format='[SIMLOG] %(levelname)s - %(message)s',
                    filemode='w',
                    filename='sim.log',
                    )


class FrontDesk:

    def __init__(self, config):
        """
               Initializes the schedule and begins simulation of scheduling
        """
        self._log = logger
        self.conf = config[0]
        # create list of days , each with their own schedule
        self.curr_day = 0
        self.days = []
        self.day_cycle = 0
        self.day_cycle_ctr = 0
        self.days_in_cycle = self.conf['days_in_cycle']

        # create days with their corresponding cycle day (day in the week)
        self.initialize_days()

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

        # initialize metrics trackers
        self.metrics = BasicMetrics()
        self.tracker = PatientMetrics()
        self.appt_tracker = ApptMetrics()

    ''' Simulation Code '''

    def initialize_days(self):
        for i in range(0, self.conf['scheduling_horizon'] + 1):
            if self.day_cycle_ctr % self.days_in_cycle == 0:
                self.day_cycle_ctr = 0
            self.days.append(Day(i, self.day_cycle_ctr))
        # reset cycle day counter
        self.day_cycle_ctr = 0

    def advance_day(self):
        '''
        Simulates the advancement of a day in the schedule.  Goes through and opens up slots
        after each day for the specified range of days.  Also updates cycle and day information vars.
        :return:
        '''

        self._log.info("Day: {} {}".format(self.curr_day, self.days[self.curr_day].day_in_cycle))

        self.simulate_appointments()

        # release slots in specified day range

        self.release_slots()

        # update fd status vals
        self.curr_day += 1
        self.day_cycle_ctr += 1

        if self.curr_day % 7 == 0:
            self.day_cycle_ctr = 1
            self.day_cycle += 1
            print "\n>>> Week (cycle) {} has finished.".format(self.day_cycle - 1)

        # update patients
        self.update_patients()

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
            for i in range(appt_start, appt_end):
                schedule[i].time = i
                schedule[i].appt = appt
                schedule[i].open = False

            # update patient records
            appt.patient.appointments.append(appt)
            appt.patient.days_until_appt = appt.date - self.curr_day
            appt.patient.total_appts += 1
            appt.patient.state = "sick_w_appt"

            self._log.debug("SCHED: {}".format(appt))

            # update metrics
            self.scheduled_appts.append(appt)
            self.metrics.appts_scheduled += 1

            # determine if cancelling
            if prob_utilized(appt) <= random.random():
                appt.will_cancel = True
                self._log.debug("{} will not be utilized.".format(appt))

            return True
        else:
            self._log.error("Unable to schedule, t{} on day {} is filled".format(appt.time, appt.date))

            return False

    def cancel_appt(self, appt):
        """
        Cancels the appointment provided as an argument
        :param appt: the appointment to cancel
        :return:
        """
        schedule = fd.get_schedule_by_day(appt.date)
        duration = appt.duration / 15
        appt_end = appt.time + duration

        for i in range(appt.time, appt_end):
            schedule[i].appt = None
            schedule[i].open = True

        self._log.debug("Cancelled {}".format(appt))

    def simulate_appointments(self):

        last_patient = -1   # don't want to double count appts attended, so keep track of last patient attended

        for slot in self.get_schedule_by_day(self.curr_day):
            if slot.appt is not None:
                if slot.appt.patient.state == "sick_w_appt" and last_patient != slot.appt.patient.id \
                        and slot.appt.will_cancel is False:

                    self.metrics.appts_attended += 1
                    slot.appt.attended = True
                    slot.appt.patient.appts_attended += 1

                    if prob_follow_up(slot.appt.patient.sched_pref) > random.random():   # TODO: !!! fix
                        slot.appt.patient.health = True
                        slot.appt.patient.needs_appt = False
                        slot.appt.patient.state = "healthy"
                    else:
                        slot.appt.patient.state = "sick_needs_follow"
                        slot.appt.patient.needs_appt = True

                    last_patient = slot.appt.patient.id
                    self._log.debug("ATTENDED: {}".format(slot.appt))

                    # clean up patient records
                    slot.appt.patient.appointments.remove(slot.appt)
                else:
                    if last_patient != slot.appt.patient.id:
                        slot.appt.attended = False
                        slot.appt.patient.needs_appt = False
                        slot.appt.patient.state = "healthy"
                        if slot.appt in slot.appt.patient.appointments:
                            slot.appt.patient.appointments.remove(slot.appt)
                        last_patient = slot.appt.patient.id
                        self._log.debug("NOT ATTENDED: {}".format(slot.appt))

    def update_patients(self):
        """
        Updates a Patient's time until appt as well as health
        :return:
        """

        for patient in self.patients:

            if len(patient.appointments) > 0:
                for appt in patient.appointments:
                    if appt.attended is False and appt.date < self.curr_day:
                        appt.days_since_request += 1
                    if appt.will_cancel is True:
                        if random.random() < 0.16:   # TODO: Get solid # for this, num based on approx from data
                            self.cancel_appt(appt)

            # flip health if random chance of sickness is satisfied
            # day in cycle determines chance of the person calling
            if determine_health(self.chance_of_call[self.days[self.curr_day].day_in_cycle]):
                patient.switch_health()

            if patient.health is False and patient.state in ['sick_needs_appt', 'sick_needs_follow']:
                self.metrics.daily_requests += 1

                self.healthy_to_sick_pool(patient=patient)

                # loop through patient's schedule preferences and attempt to satisfy one
                scheduled = False
                policy = getattr(fd, self.conf['policy'])

                for i in range(0, patient.sched_pref):
                    if scheduled is False:
                        appt = Appointment(patient=patient,
                                           date=(self.curr_day + i),
                                           time=policy(self.curr_day + i if self.curr_day + i < len(self.days) else -1),
                                           duration=(15 * random.randint(1, 4)),
                                           scheduled_on=self.curr_day)

                        # schedule the appointment they want if we can
                        if self.check_appt(appt) and scheduled is False:
                            self.schedule_appt(appt)
                            scheduled = True
                            patient.state = "sick_w_appt"

                # patient is lost
                if scheduled is False:
                    self.sick_to_healthy_pool(patient=patient)
                    patient.needs_appt = False
                    patient.health = True
                    patient.state = "healthy"

                    self._log.debug("SCHED FAILED: {}".format(patient))
                    self.metrics.appts_not_scheduled += 1

            else:
                self.sick_to_healthy_pool(patient=patient)

    def release_slots(self):
        for day in [1, 3, 7, 14, 28]:

            if self.curr_day + day < len(self.days):

                release_day = self.days[self.curr_day + day]

                first_closed = release_day.get_first_closed_slot()
                fc_index = release_day.schedule.index(first_closed)
                for i in range(fc_index, int(fc_index + (self.release_schedule[day]) * 32) - 1):
                    if release_day.day_num < len(self.days) - 1:
                        # self._log.debug("Opening slot : Day {} {}".format(release_day.day_num, release_day.schedule[i]))
                        release_day.schedule[i].open = True

    '''Scheduling Policies'''

    def get_first_avail(self, day):
        """
        Gets first available slot in the day
        :param day: day to get first avail slot from
        :return: timeslot # of first open, else -1
        """
        # go through times in the day
        if day == -1:
            return -1

        for slot in self.days[day].schedule:
            # if slot is available, return slot time
            if slot.appt is None and slot.open is True:
                return slot.time
        return -1

    '''Helper Functions'''

    def get_patients_info(self):
        for patient in self.patients:
            print "ID: {} -- State: {} --- Days Until Appt: {} ".format(patient.id, patient.state, (
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

    def get_schedule_by_day(self, day_num):
        """
        Gets the schedule of the specified day

        :param day_num: the day to get the schedule for
        :return: the schedule of the day specified

        """

        return self.days[day_num].schedule

    def sick_to_healthy_pool(self, patient):
        if patient not in self.sick:
            self.sick.append(patient)
        if patient in self.healthy:
            self.healthy.remove(patient)

    def healthy_to_sick_pool(self, patient):
        if patient in self.sick:
            self.sick.remove(patient)
        if patient not in self.healthy:
            self.healthy.append(patient)

''' outside helper functions '''

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
        if patient.state in ['sick_needs_appt', 'sick_needs_follow']:
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


def prob_utilized(appt):
    b_0 = 0.51517
    b_1 = 0.201328
    b_2 = 0.146079
    B_1 = 1.1486
    B_2 = 0.0356
    t = appt.days_since_request

    y = b_0 + math.fsum([b_1 * math.pow(math.e, (-B_1 * t)), b_2 * math.pow(math.e, (-B_2 * t))])

    return y


def prob_follow_up(t):
    A = 0.57013
    a = 0.0273

    p = A*(1-math.pow(math.e, -a*t))

    return p

def run_simulation(length, sim_num):
    for day in range(0, length):
        # simulate day and append metrics to df
        fd.advance_day()
        appt_ctr = 0
        for slot in fd.days[fd.curr_day].schedule:
            if slot.appt is not None:
                appt_ctr += 1

        fd.metrics.append_to_df(day)

    fd.tracker.append_to_df(fd.patients)
    fd.appt_tracker.append_to_df(fd.scheduled_appts)

    writer = pd.ExcelWriter("../metrics/Metrics_Run_{}.xlsx".format(sim_num), engine="xlsxwriter")
    fd.metrics.metrics_df.to_excel(writer, "Simulation Data")
    fd.tracker.metrics_df.to_excel(writer, "Patient Data")
    fd.appt_tracker.metrics_df.to_excel(writer, "Appointment Data")

    sim_fd = fd.metrics.metrics_df[['Appts Scheduled','Appts. Attended']].copy()

    sim_fd.to_excel(writer, sheet_name="Test")

    wb = writer.book
    ws = writer.sheets["Test"]

    chart = wb.add_chart({'type': 'line'})

    max_row = 180

    for i in range(2):
        col = i + 1
        chart.add_series({
            'name': ["Test", 0, col],
            'categories': ["Test", 1, 0, max_row, 0],
            'values': ["Test", 1, col, max_row, col],
        })

    chart.set_x_axis({'name': 'Days'})
    chart.set_y_axis({'name': 'Appointments', 'major_gridlines': {'visible': True}})

    ws.insert_chart("G2", chart)

    writer.save()


if __name__ == "__main__":

    configs = conf.get_configs()
    for i in range(len(configs)):
        fd = FrontDesk(config=configs[i])
        patients = fd.patients
        print configs[i]
        run_simulation(fd.conf['scheduling_horizon'], i)
