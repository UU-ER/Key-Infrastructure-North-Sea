import case_study_data.optimization.utilities as pp
import numpy as np
from src.model_configuration import ModelConfiguration
from src.energyhub import EnergyHub
import pandas as pd
import random

# General Settings
save_path = 'PATH'
save_path_test = 'PATH_TEST'

# To test the code set test = 1
settings = pp.Settings(test=1)
pp.write_to_technology_data(settings)
pp.write_to_network_data(settings)

emission_targets = [0.99, 0.98, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0]
emission_targets.reverse()

h2_emissions = 29478397.12

baseline_emissions = 56314060.91 + h2_emissions

settings.demand_factor = 1

scenarios = {'Baseline': 'Baseline',
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

    max_em_reduction = None
    min_cost = None

    print(stage)
    print(max_em_reduction)


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
        configuration.reporting.save_path = save_path_test
        configuration.reporting.save_summary_path = save_path_test
    else:
        configuration.reporting.save_path = save_path
        configuration.reporting.save_summary_path = save_path

    # Construct model
    energyhub = EnergyHub(data, configuration)
    energyhub.construct_model()
    energyhub.construct_balances()

    # Min Cost
    if min_cost is None:
        energyhub.configuration.optimization.objective = 'costs'

        if settings.test == 1:
            energyhub.configuration.reporting.case_name = 'TEST' + stage + '_costs'
        else:
            energyhub.configuration.reporting.case_name = stage + '_costs'

        energyhub.solve()
        min_cost = energyhub.model.var_total_cost.value

    if stage != 'Baseline':

        if max_em_reduction is None:
            # Min Emissions
            energyhub.configuration.optimization.objective = 'emissions_net'
            if settings.test == 1:
                energyhub.configuration.reporting.case_name = 'TEST' + stage + '_minE'
            else:
                energyhub.configuration.reporting.case_name = stage + '_minE'
            energyhub.solve()
            max_em_reduction = (energyhub.model.var_emissions_net.value + h2_emissions) / baseline_emissions

        # Emission Reductions
        for reduction in emission_targets:
            energyhub.configuration.optimization.objective = 'costs_emissionlimit'
            if max_em_reduction <= reduction:
                energyhub.configuration.optimization.emission_limit = baseline_emissions * reduction - h2_emissions
                if settings.test == 1:
                    energyhub.configuration.reporting.case_name = 'TEST' + stage + '_minCost_at_' + str(reduction)
                else:
                    energyhub.configuration.reporting.case_name = stage + '_minCost_at_' + str(reduction)
                energyhub.solve()

