import pandas as pd

def get_configs():
    df = pd.read_excel("../SchedSimConfig.xlsx", sheet_name="conf")

    configs = []

    for num in range(len(df)):
        simulation = dict(scheduling_horizon=df.SchedHorizon[num],
                          num_patients=df.Patients[num],
                          policy=str(df.Policy[num]),
                          num_sims=df.Sims[num],
                          days_in_cycle=df.DaysInCycle[num])

        rel_schedule = {
                        1: df.PctRel1[num],
                        3: df.PctRel3[num],
                        7: df.PctRel7[num],
                        14: df.PctRel14[num],
                        28: df.PctRel28[num]
                        }
        configs.append([simulation, rel_schedule])

    return configs


