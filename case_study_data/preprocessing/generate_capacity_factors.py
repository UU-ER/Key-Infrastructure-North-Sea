import pandas as pd

# CAPACITY FACTORS
def calculate_cap_factors(caps_type, re_profiles, save_path, tec):
    cap_factors = pd.DataFrame()
    for idx, row in caps_type.iterrows():
        node = row['Node']
        re_profile = re_profiles[(node, tec)]

        if tec != 'Wind offshore':
            cap = row['Capacity our work']
        else:
            cap = re_profile.max()

        cap_factors[node] = re_profile/cap

    cap_factors.to_csv(save_path)
    print(cap_factors.max())
    print(cap_factors.mean())


re_profiles = pd.read_csv('./case_study_data/clean_data/production_profiles_re/production_profiles_re.csv', header=[0,1])
caps = pd.read_csv('./case_study_data/clean_data/installed_capacities/capacities_node.csv', index_col=[0])

calculate_cap_factors(caps[caps['Technology'] == 'Solar'], re_profiles, './case_study_data/clean_data/capacity_factors/pv.csv', 'PV')
calculate_cap_factors(caps[caps['Technology'] == 'Wind Onshore'], re_profiles, './case_study_data/clean_data/capacity_factors/wind_onshore.csv', 'Wind onshore')
# calculate_cap_factors(caps[caps['Technology'] == 'Wind Offshore'], re_profiles, './case_study_data/clean_data/capacity_factors/wind_offshore.csv', 'Wind offshore')
