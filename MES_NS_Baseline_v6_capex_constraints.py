import mes_north_sea.optimization.utilities as pp
import numpy as np
from src.model_configuration import ModelConfiguration
from src.energyhub import EnergyHub
import pandas as pd
import random
import pyomo.environ as pyo

# General Settings
settings = pp.Settings(test=1)
pp.write_to_technology_data(settings)
pp.write_to_network_data(settings)

# in mio
investment_targets = [2000, 4000, 6000, 8000, 10000, 12000, 14000]


h2_emissions = 29478397.12

baseline_emissions = 56314060.91 + h2_emissions

prev_results = pd.read_excel('//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/baseline_demand_v6/Summary.xlsx')
prev_results = prev_results[prev_results['objective'] == 'emissions_minC']

settings.demand_factor = 1

scenarios = {
              'Battery_on': 'Battery (onshore only)',
              'Battery_off': 'Battery (offshore only)',
              'Battery_all': 'Battery (all)',
              'Battery_all_HP': 'Battery (all, high power-energy-ratio)',
              'ElectricityGrid_all': 'Grid Expansion (all)',
              'ElectricityGrid_on': 'Grid Expansion (onshore only)',
              'ElectricityGrid_off': 'Grid Expansion (offshore only)',
              'ElectricityGrid_noBorder': 'Grid Expansion (no Border)',
              'Hydrogen_Baseline': 'Hydrogen (all)',
              'Hydrogen_H1': 'Hydrogen (no storage)',
              'Hydrogen_H2': 'Hydrogen (no hydrogen offshore)',
              'Hydrogen_H3': 'Hydrogen (no hydrogen onshore)',
              'Hydrogen_H4': 'Hydrogen (local use only)',
              'All': 'All Pathways'
             }

for stage in scenarios.keys():

    # THIS IS ONLY NEEDED IF PREVIOUS RESULTS ARE THERE
    if prev_results['time_stamp'].str.contains(stage).any():
        max_em_reduction = (prev_results[prev_results['time_stamp'].str.contains(stage)]['net_emissions'].values[0] + h2_emissions)/ baseline_emissions
        min_cost = prev_results[prev_results['time_stamp'].str.contains(stage)]['total_costs'].values[0]
    else:
        max_em_reduction = None
        min_cost = None

    print(stage)
    print(max_em_reduction)

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
        configuration.reporting.save_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/baseline_demand_v6/'
        configuration.reporting.save_summary_path = '//ad.geo.uu.nl/Users/StaffUsers/6574114/EhubResults/MES NorthSea/baseline_demand_v6/'

    # Construct model
    energyhub = EnergyHub(data, configuration)
    energyhub.construct_model()
    energyhub.construct_balances()
    #
    # # Min Cost
    # if min_cost is None:
    #     energyhub.configuration.optimization.objective = 'costs'
    #
    #     if settings.test == 1:
    #         energyhub.configuration.reporting.case_name = 'TEST' + stage + '_costs'
    #     else:
    #         energyhub.configuration.reporting.case_name = stage + '_costs'
    #
    #     energyhub.solve()
    #     min_cost = energyhub.model.var_total_cost.value
    #
    # # Min Emissions
    # if stage != 'Baseline':
    #     energyhub.configuration.optimization.objective = 'emissions_net'
    #     if settings.test == 1:
    #         energyhub.configuration.reporting.case_name = 'TEST' + stage + '_minE'
    #     else:
    #         energyhub.configuration.reporting.case_name = stage + '_minE'
    #     energyhub.solve()
    #     max_em_reduction = (energyhub.model.var_emissions_net.value + h2_emissions) / baseline_emissions

    # Investments target
    print(stage)
    for investment in investment_targets:
        def init_capex_const(const):
            tec_capex = sum(
                sum(energyhub.model.node_blocks[node].tech_blocks_active[
                        tec].var_capex_upfront
                    for tec in energyhub.model.node_blocks[node].set_tecsAtNode)
                for node in energyhub.model.set_nodes)
            netw_capex = sum(energyhub.model.network_block[netw].var_capex_upfront
                             for netw in energyhub.model.set_networks)
            if "ElectricityGrid" in stage:
                return tec_capex + netw_capex <= investment *10^6
            else:
                return tec_capex + netw_capex == investment *10^6

        if energyhub.model.find_component('const_capex_target'):
            energyhub.model.del_component(energyhub.model.const_capex_target)

        energyhub.model.const_capex_target = pyo.Constraint(rule=init_capex_const)
        energyhub.configuration.optimization.objective = 'costs'

        if settings.test == 1:
            energyhub.configuration.reporting.case_name = ('TEST' + stage +
                                                           '_capex_target_' +
                                                           str(investment))
        else:
            energyhub.configuration.reporting.case_name = (stage +
                                                           '_capex_target_' +
                                                           str(investment))
        energyhub.solve()


