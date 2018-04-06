import pandas as pd

def get_conf(num):
    df = pd.read_excel("../SchedSimConfig.xlsx", sheet_name="conf")

    simulation = dict(scheduling_horizon=df.SchedHorizon[num],
                      num_patients=df.Patients[num],
                      policy=str(df.Policy[num]),
                      num_sims=df.Sims[num])

    rel_schedule = {
                    1: df.PctRel1[num],
                    3: df.PctRel3[num],
                    7: df.PctRel7[num],
                    14: df.PctRel14[num],
                    28: df.PctRel28[num]
                    }

    return simulation, rel_schedule


simulation , release_schedule = get_conf(0)

