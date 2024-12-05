from ..components.technologies.genericTechnologies.res import Res
import pandas as pd
import numpy as np

class Res_Cap(Res):
    def __init__(self,
                tec_data):
        super().__init__(tec_data)

    def fit_technology_performance(self, node_data):
        node = node_data.name
        max_caps = pd.read_csv('./input_data/clean_data/max_re_cap/max_re_nodes.csv')

        # read in data
        if self.name == 'Offshore_Wind':
            self.size_max = min(max_caps[max_caps['Node'] == node][
                'RemainingPotential_Wind_off'].values[0], 250000/2)
            capacity_factor = pd.read_csv('./input_data/clean_data/capacity_factors/wind_offshore.csv')
        elif self.name == 'Onshore_Wind':
            self.size_max = min(max_caps[max_caps['Node'] == node][
                'RemainingPotential_Wind_on'].values[0], 100000)
            capacity_factor = pd.read_csv('./input_data/clean_data/capacity_factors/wind_onshore.csv')
        elif self.name == 'PV':
            self.size_max = min(max_caps[max_caps['Node'] == node][
                'RemainingPotential_PV'].values[0], 400000)
            capacity_factor = pd.read_csv('./input_data/clean_data/capacity_factors/pv.csv')

        capacity_factor = capacity_factor[node].values

        # read in cap factors
        self.fitted_performance.bounds['output']['electricity'] = np.column_stack((np.zeros(shape=(len(capacity_factor))), self.size_max * capacity_factor.round(3)))
        # Coefficients
        self.fitted_performance.coefficients['capfactor'] = capacity_factor.round(3)
        # Time dependent coefficents
        self.fitted_performance.time_dependent_coefficients = 1


