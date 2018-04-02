import pandas as pd
import numpy as np


class BasicMetrics:

    def __init__(self):
        self.appts_scheduled = 0
        self.appts_not_scheduled = 0
        self.daily_requests = 0
        self.appts_attended = 0
        self.sick_to_healthy_ratio = 0.0

        self.indicies = ["Appts Scheduled",
                    "Appts Not Scheduled",
                    "Appt Requests",
                    "Appts. Attended",
                    "Sick/Healthy Ratio"]

        self.metrics_df = pd.DataFrame(columns=self.indicies)
        pd.set_option("max_colwidth", 50)

    def append_metrics_to_df(self, day):

        data = [self.appts_scheduled, self.appts_not_scheduled,
                self.daily_requests, self.appts_attended,
                self.sick_to_healthy_ratio]

        self.metrics_df.loc[day] = data

    def reset_daily_values(self):
        self.appts_scheduled = 0
        self.appts_not_scheduled = 0
        self.appts_attended = 0
        self.daily_requests = 0


class PatientMetrics:

    def __init__(self):

        self.indicies = ["Days Until Appt",
                         "Appointments Scheduled",
                         "Appts. Attended"]

        self.metrics_df = pd.DataFrame(columns=self.indicies)
        pd.set_option("max_colwidth", 50)

    def append_metrics_to_df(self, patients):
        ids = []
        for i in range(len(patients)):
            ids.append(i)
        for patient in patients:
            ids.append(patient.id)
            data = [patient.days_until_appt, patient.total_appts, patient.appts_attended]

            self.metrics_df.loc[patient.id] = data




