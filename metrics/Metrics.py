import pandas as pd
import numpy as np


class BasicMetrics:
    def __init__(self):
        self.appts_scheduled = 0
        self.appts_not_scheduled = 0
        self.daily_requests = 0
        self.appts_attended = 0
        self.appts_not_utilized = 0
        self.appts_cancelled = 0

        self.indicies = [ "Appt Requests", "Appts Scheduled", "Appts Not Scheduled",
                         "Appts. Attended", "Appts. Not Utilized", "Appts. Cancelled"]

        self.metrics_df = pd.DataFrame(columns=self.indicies)
        pd.set_option("max_colwidth", 50)

    def append_to_df(self, day):
        data = [self.daily_requests, self.appts_scheduled, self.appts_not_scheduled,
                self.appts_attended, self.appts_not_utilized, self.appts_cancelled]

        self.metrics_df.loc[day] = data

    def reset_daily_values(self):
        self.appts_scheduled = 0
        self.appts_not_scheduled = 0
        self.appts_attended = 0
        self.daily_requests = 0
        self.appts_not_utilized = 0
        self.appts_cancelled = 0


class PatientMetrics:
    def __init__(self):

        self.indicies = ["Days Until Appt",
                         "Appointments Scheduled",
                         "Appts. Attended"]

        self.metrics_df = pd.DataFrame(columns=self.indicies)
        pd.set_option("max_colwidth", 50)

    def append_to_df(self, patients):
        ids = []
        for i in range(len(patients)):
            ids.append(i)
        for patient in patients:
            ids.append(patient.id)
            data = [patient.days_until_appt, patient.total_appts, patient.appts_attended]

            self.metrics_df.loc[patient.id] = data


class ApptMetrics:
    def __init__(self):
        self.indicies = ["Sched On",
                         "Sched For",
                         "Length",
                         "Attended?"]

        self.metrics_df = pd.DataFrame(columns=self.indicies)
        pd.set_option("max_colwidth", 50)

    def append_to_df(self, appts):
        appt_ctr = 1
        for appt in appts:
            data = pd.Series({self.indicies[0]: appt.scheduled_date,
                              self.indicies[1]: appt.date,
                              self.indicies[2]: appt.duration,
                              self.indicies[3]: appt.attended})

            self.metrics_df.loc[appt_ctr] = data
            appt_ctr += 1
