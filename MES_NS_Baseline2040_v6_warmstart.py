import mes_north_sea.optimization.utilities as pp
import numpy as np
from src.model_configuration import ModelConfiguration
from src.energyhub import EnergyHub
import pandas as pd
import random
import pyomo.environ as pyo

# General Settings
testing = 0
settings = pp.Settings(test=testing)
settings.year = 2040
settings.simplify_networks = 1

pp.write_to_technology_data(settings)
pp.write_to_network_data(settings)

emission_targets = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0]
emission_targets.reverse()

if testing:
    h2_emissions = 81796113.3 *(3/365)
else:
    h2_emissions = 81796113.3

baseline_emissions = 56314060.91 + h2_emissions

# prev_results = pd.read_excel('//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/baseline_demand_v6/Summary.xlsx')
# prev_results = prev_results[prev_results['objective'] == 'emissions_minC']

settings.demand_factor = 1


# scenarios = {
#               'All': 'All Pathways',
#              }
scenarios = {
            # 'Hydrogen_H2': 'Hydrogen (no hydrogen offshore)',
            # 'Hydrogen_H1': 'Hydrogen (no storage)',
            # 'Hydrogen_H4': 'Hydrogen (local use only)',
            # 'Hydrogen_Baseline': 'Hydrogen (all)',
            'Hydrogen_H3': 'Hydrogen (no hydrogen onshore)',
            # 'All': 'All Pathways',
            #
            # 'ElectricityGrid_all': 'Grid Expansion (all)',
            # 'ElectricityGrid_on': 'Grid Expansion (onshore only)',
            # 'ElectricityGrid_off': 'Grid Expansion (offshore only)',
            # 'ElectricityGrid_noBorder': 'Grid Expansion (no Border)',
            # 'RE_only': 'RE only',
            # 'Battery_on': 'Battery (onshore only)',
            # 'Battery_off': 'Battery (offshore only)',
            # 'Battery_all': 'Battery (all)',
            #
            # 'RE_only_no_onshore_wind': 'RE only - no onshore wind',
            # 'Battery_on_no_onshore_wind': 'Battery (onshore only) - no onshore wind',
            # 'Battery_off_no_onshore_wind': 'Battery (offshore only) - no onshore wind',
            # 'Battery_all_no_onshore_wind': 'Battery (all) - no onshore wind',
            # 'ElectricityGrid_all_no_onshore_wind': 'Grid Expansion (all) - no onshore wind',
            # 'Hydrogen_Baseline_no_onshore_wind': 'Hydrogen (all) - no onshore wind',
            # 'Hydrogen_H1_no_onshore_wind': 'Hydrogen (no storage) - no onshore wind',
            # 'Hydrogen_H2_no_onshore_wind': 'Hydrogen (no hydrogen offshore) - no onshore wind',
            # 'Hydrogen_H3_no_onshore_wind': 'Hydrogen (no hydrogen onshore) - no onshore wind',
            # 'Hydrogen_H4_no_onshore_wind': 'Hydrogen (local use only) - no onshore wind',
            # 'All_no_onshore_wind': 'All Pathways - no onshore wind'
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
        configuration.reporting.save_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/2040_demand_v6_simplifiedgrids/'
        configuration.reporting.save_summary_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/2040_demand_v6_simplifiedgrids/'

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

    # Formulate constraint on total costs
    # if stage == "Hydrogen_Baseline":
    #     energyhub.model.const_objective_low = pyo.Constraint(
    #         expr=energyhub.model.var_total_cost <= 29933953054+1000)
    #
    # if stage == "All":
    #     energyhub.model.const_objective_low = pyo.Constraint(
    #         expr=energyhub.model.var_total_cost <= 24478323952+1000)
    #
    # if stage == "Hydrogen_H3":
    #     energyhub.model.const_objective_low = pyo.Constraint(
    #         expr=energyhub.model.var_total_cost <= 32423541620+1000)

    # if "ElectricityGrid" in stage:
    #     energyhub.model.const_objective_up = pyo.Constraint(
    #         expr=energyhub.model.var_total_cost >= 24670382918)
    #
    # if "Hydrogen" in stage:
    #     energyhub.model.const_objective_up = pyo.Constraint(
    #         expr=energyhub.model.var_total_cost >= 30074314187)

    energyhub.fix_design("//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/2040_demand_v6_simplifiedgrids/20240829084757_RE_only_costs/optimization_results.h5", 1)
    energyhub.solve()

    energyhub.unfix_design()
    energyhub.fix_design("//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/2040_demand_v6_simplifiedgrids/20240829084757_RE_only_costs/optimization_results.h5", 0)
    energyhub.solve()

    energyhub.unfix_design()
    energyhub.solve()
    # energyhub.model.del_component(energyhub.model.const_objective_low)
    # if "ElectricityGrid" in stage:
    #     energyhub.model.del_component(energyhub.model.const_objective_up)

    #
    # if stage == 'All':
    #     baseline_emissions = energyhub.model.var_emissions_net.value + h2_emissions
    # #
    # # Min Emissions
    # energyhub.configuration.optimization.objective = 'emissions_net'
    # if settings.test == 1:
    #     energyhub.configuration.reporting.case_name = 'TEST' + stage + '_minE'
    # else:
    #     energyhub.configuration.reporting.case_name = stage + '_minE'
    #
    # energyhub.model.const_objective_low = pyo.Constraint(
    #     expr=energyhub.model.var_emissions_net <= 2064544.3)
    #
    # if "ElectricityGrid" in stage:
    #     energyhub.model.const_objective_up = pyo.Constraint(
    #         expr=energyhub.model.var_emissions_net >= 0)
    #
    # energyhub.solve()
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
