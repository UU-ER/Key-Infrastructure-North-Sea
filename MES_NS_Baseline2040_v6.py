import mes_north_sea.optimization.utilities as pp
import numpy as np
from src.model_configuration import ModelConfiguration
from src.energyhub import EnergyHub
import pandas as pd
import random

# General Settings
settings = pp.Settings(test=1)
settings.year = 2040
pp.write_to_technology_data(settings)
pp.write_to_network_data(settings)

emission_targets = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0]
emission_targets.reverse()

h2_emissions = 81796113297

# baseline_emissions = 56314060.91 + h2_emissions

# prev_results = pd.read_excel('//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/baseline_demand_v6/Summary.xlsx')
# prev_results = prev_results[prev_results['objective'] == 'emissions_minC']

settings.demand_factor = 1

# scenarios = {'RE_only': 'RE_only',
#               'Battery_all': 'Battery (all)',
#               'ElectricityGrid_all': 'Grid Expansion (all)',
#               'Hydrogen_Baseline': 'Hydrogen (all)',
#               'All': 'All Pathways',
#               'RE_only_no_onshore_wind': 'RE_only (no onshore wind)', # infeasible
#               'Battery_all_no_onshore_wind': 'Battery (all, no onshore wind)',
#               'ElectricityGrid_all_no_onshore_wind': 'Grid Expansion (all, no onshore wind)', # infeasible
#               'Hydrogen_Baseline_no_onshore_wind': 'Hydrogen (all, no onshore wind)',
#               'All_no_onshore_wind': 'All Pathways (no onshore wind)',
#              }

scenarios = {
              'Battery_all_no_onshore_wind': 'Battery (all, no onshore wind)',
              'Hydrogen_Baseline_no_onshore_wind': 'Hydrogen (all, no onshore wind)',
              'All_no_onshore_wind': 'All Pathways (no onshore wind)',
             }


for stage in scenarios.keys():

    # # THIS IS ONLY NEEDED IF PREVIOUS RESULTS ARE THERE
    # if prev_results['time_stamp'].str.contains(stage).any():
    #     max_em_reduction = (prev_results[prev_results['time_stamp'].str.contains(stage)]['net_emissions'].values[0] + h2_emissions)/ baseline_emissions
    #     min_cost = prev_results[prev_results['time_stamp'].str.contains(stage)]['total_costs'].values[0]
    # else:
    # max_em_reduction = None
    # min_cost = None
    #
    # print(stage)
    # print(max_em_reduction)

    # if stage != 'Baseline':

    # THIS IS WHERE WE REALLY START
    settings.new_technologies_stage = stage

    # Configuration
    configuration = pp.define_configuration()

    # Set Data
    nodes = pp.read_nodes(settings)
    topology = pp.define_topology(settings, nodes)
    topology = pp.define_installed_capacities(settings, nodes, topology)
    topology = pp.define_networks(settings, topology)
    topology = pp.define_new_technologies(settings, nodes, topology)

    data = pp.define_data_handle(topology, nodes)
    data = pp.define_generic_production(settings, nodes, data)
    data = pp.define_hydro_inflow(settings, nodes, data)
    data = pp.define_demand(settings, nodes, data)
    data = pp.define_imports_exports(settings, nodes, data)

    # Read data
    data.read_technology_data(load_path = settings.tec_data_path)
    data.read_network_data(load_path=settings.netw_data_path)
    data = pp.define_charging_efficiencies(settings, nodes, data)

    # Alter capex of technologies to remove symmetry
    for node in data.technology_data:
        for tec in data.technology_data[node]:
            data.technology_data[node][tec].economics.capex_data['unit_capex'] = data.technology_data[node][tec].economics.capex_data['unit_capex'] * random.uniform(0.99, 1.01)

    if settings.test == 1:
        configuration.reporting.save_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/tests/'
        configuration.reporting.save_summary_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/tests/'
    else:
        configuration.reporting.save_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/2040_demand_v6/'
        configuration.reporting.save_summary_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/2040_demand_v6/'

    # Construct model
    energyhub = EnergyHub(data, configuration)
    energyhub.construct_model()
    energyhub.construct_balances()

    # Min Cost
    energyhub.configuration.optimization.objective = 'costs'

    if settings.test == 1:
        energyhub.configuration.reporting.case_name = 'TEST' + stage + '_costs'
    else:
        energyhub.configuration.reporting.case_name = stage + '_costs'

    energyhub.solve()
    min_cost = energyhub.model.var_total_cost.value

    # if stage == 'RE_only':
    #     baseline_emissions = energyhub.model.var_emissions_net.value + h2_emissions

    # Min Emissions
    energyhub.configuration.optimization.objective = 'emissions_net'
    if settings.test == 1:
        energyhub.configuration.reporting.case_name = 'TEST' + stage + '_minE'
    else:
        energyhub.configuration.reporting.case_name = stage + '_minE'
    energyhub.solve()
    # max_em_reduction = (energyhub.model.var_emissions_net.value + h2_emissions) / baseline_emissions

    # # Emission Reductions
    # for reduction in emission_targets:
    #     energyhub.configuration.optimization.objective = 'costs_emissionlimit'
    #     if max_em_reduction <= reduction:
    #         energyhub.configuration.optimization.emission_limit = baseline_emissions * reduction - h2_emissions
    #         if settings.test == 1:
    #             energyhub.configuration.reporting.case_name = 'TEST' + stage + '_minCost_at_' + str(reduction)
    #         else:
    #             energyhub.configuration.reporting.case_name = stage + '_minCost_at_' + str(reduction)
    #         energyhub.solve()

