import pandas as pd
import numpy as np

class BasicMetrics:

    def __init__(self):
        self.appts_scheduled = 0
        self.appts_not_scheduled = 0

        self.requests_total = 0
        self.lost_patients = 0

        self.appts_attended = 0

        self.wrt = pd.ExcelWriter("Metrics.xlsx",
                                  engine="xlsxwriter")

        self.indicies = ["Appts Scheduled",
                    "Appts Not Scheduled",
                    "Total Appt Requests",
                    "Appts. Attended",
                    "Total Lost Patients"]

        self.metrics_df = pd.DataFrame(columns=self.indicies)
        pd.set_option("max_colwidth", 50)

    def append_metrics_to_df(self, day):


        data = [self.appts_scheduled, self.appts_not_scheduled,
                self.requests_total, self.appts_attended, self.lost_patients]

        self.metrics_df.loc[day] = data







