import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path
import folium
from streamlit_folium import st_folium
import h5py
import numpy as np

from plot_networks import *
from utilities import *
from read_data import *
from plotting import *

st.set_page_config(layout="wide")

# Data required
root = 'src/case_offshore_storage/visualization_v2/'
re_gen_path = root + 'data/production_profiles_re.csv'
result_path = root + 'data/cases/'
case_keys = root + 'data/Cases.csv'
cases_available = pd.read_csv(case_keys, sep=';')
summary_df = pd.read_excel('./src/case_offshore_storage/visualization_v2/data/Summary_Plotting6_processed.xlsx')
summary_df['FuelCell_h2_input'] = summary_df['FuelCell_el_output'] / 0.5
h2_case = summary_df[summary_df['Case'] == 'Hydrogen']
min_cost = h2_case[h2_case['Emission Reduction'] == 'Min cost'].fillna(0)
min_emission = h2_case[h2_case['Emission Reduction'] == 'Min emissions'].fillna(0)

baseline =  summary_df[summary_df['Case'] == 'Baseline'].fillna(0)

st.header('The role of hydrogen')
st.subheader('Technology sizes for different scenarios at minimum costs')
#
# # Emission Reduction
# plot_er = min_cost[['Subcase', 'emission_reduction']].melt(id_vars=['Subcase'])
# plot_er['value'] = (1-plot_er['value'])*100
# plot_er_base = plot_er[plot_er['Subcase'] == 'all']
#
# # Sizes
# plot_s = min_cost[['Subcase', 'Electrolyser_PEM_size', 'Electrolyser_PEM_offshore_size', 'FuelCell_size', 'Storage_Hydrogen_size']].melt(id_vars=['Subcase'], var_name='Technology')
# plot_s['Location'] = np.where(plot_s['Technology'].str.contains('Electrolyser_PEM_size'), 'onshore',
#                                     np.where(plot_s['Technology'].str.contains('Electrolyser_PEM_offshore_size'), 'offshore', 'onshore'))
# plot_s['Technology'] = np.where(plot_s['Technology'].str.contains('Electrolyser'), 'Electrolyser',
#                                     np.where(plot_s['Technology'].str.contains('FuelCell'), 'Fuel Cell', 'Storage'))
# plot_s['value'] = plot_s['value']/1000
# plot_s_base = plot_s[plot_s['Subcase'] == 'all']
#
# max_size = max(plot_s['value'])
#
# # Abatement Costs
# plot_c = min_cost[['Subcase', 'abatemente_cost']].melt(id_vars=['Subcase'])
# plot_c_base = plot_c[plot_c['Subcase'] == 'all']
#
# min_c = min(plot_c['value'])
#
# for case in plot_s['Subcase'].unique():
#     st.markdown("**" + case + "**")
#
#     # Emission Reduction
#     plot_case = plot_er[(plot_er['Subcase'] == case)]
#     bar_er = alt.Chart(plot_case).mark_bar().encode(
#         x=alt.X('sum(value)', scale=alt.Scale(zero=True, domainMax=7), title='Emission Reduction (%)'),
#         color=alt.value('red')
#     ).interactive()
#
#     point_er = alt.Chart(plot_er_base).mark_point().encode(
#         x=alt.X('sum(value)', scale=alt.Scale(zero=True, domainMax=7), title='Emission Reduction (%)'),
#         color = alt.value('black')
#     ).interactive()
#
#     chart_er = alt.layer(bar_er, point_er)
#
#     # Abatement Cost
#     plot_case = plot_c[(plot_c['Subcase'] == case)]
#     bar_c = alt.Chart(plot_case).mark_bar().encode(
#         x=alt.X('sum(value)', scale=alt.Scale(domain=(min_c, 0)), title='Abatement Cost (EUR/t)'),
#         color=alt.value('lightblue')
#     ).interactive()
#
#     point_c = alt.Chart(plot_c_base).mark_point().encode(
#         x=alt.X('sum(value)', scale=alt.Scale(zero=True, domainMax=7), title='Emission Reduction (%)'),
#         color = alt.value('black')
#     ).interactive()
#     chart_c = alt.layer(bar_c, point_c)
#
#     # Sizes
#     plot_case = plot_s[(plot_s['Subcase'] == case)]
#     bar_s = alt.Chart(plot_case).mark_bar().encode(
#         x=alt.X('sum(value)', scale=alt.Scale(zero=True, domainMax=max_size), title='Size (GW/GWh)'),
#         y=alt.Y('Technology', title=None),
#         color = 'Location'
#     ).interactive()
#
#     point_s = alt.Chart(plot_s_base).mark_point().encode(
#         x=alt.X('sum(value)', scale=alt.Scale(zero=True, domainMax=max_size), title='Size (GW/GWh)'),
#         y=alt.Y('Technology', title=None),
#         color = alt.value('black')
#     ).interactive()
#     chart_s = alt.layer(bar_s, point_s)
#
#     st.altair_chart(chart_er | chart_c | chart_s)

st.subheader('Hydrogen Use')

red_case = st.selectbox("Select a case", ["min cost", "min emissions"])

if red_case == "min cost":
    plot_data = min_cost
else:
    plot_data = min_emission

plot_data = plot_data[['Subcase', 'Total RE Generation', 'PowerPlant_Nuclear_existing_el_output', 'Electrolyser_PEM_h2_output','FuelCell_h2_input', 'Electrolyser_PEM_offshore_h2_output', 'hydrogen_input_gt', 'Hydrogen Exports']]
plot_baseline = baseline[['Subcase', 'Total RE Generation', 'PowerPlant_Nuclear_existing_el_output', 'Electrolyser_PEM_h2_output','FuelCell_h2_input', 'Electrolyser_PEM_offshore_h2_output', 'hydrogen_input_gt', 'Hydrogen Exports']]

# plot_data = min_cost[['Subcase', 'Total RE Generation', 'PowerPlant_Nuclear_existing_el_output', 'hydrogen_input_gt', 'Hydrogen Exports']]
# plot_baseline = baseline[['Subcase', 'Total RE Generation', 'PowerPlant_Nuclear_existing_el_output', 'hydrogen_input_gt', 'Hydrogen Exports']]

delta_columns = ['Total RE Generation']
for col in delta_columns:
    plot_data[delta_columns] = plot_data[delta_columns] - plot_baseline[delta_columns].values[0]

plot_data = plot_data.melt(id_vars=['Subcase'], var_name='Technology')
plot_data['value'] = plot_data['value'] / 1000000


plot_data['Side'] = np.where(plot_data['Technology'].str.contains('Total RE Generation'), 'Supply',
                        np.where(plot_data['Technology'].str.contains('PowerPlant_Nuclear_existing_el_output'), 'Supply',
                        np.where(plot_data['Technology'].str.contains('Electrolyser_PEM_h2_output'), 'Production',
                        np.where(plot_data['Technology'].str.contains('Electrolyser_PEM_offshore_h2_output'), 'Production',
                        np.where(plot_data['Technology'].str.contains('hydrogen_input_gt'), 'Demand',
                        np.where(plot_data['Technology'].str.contains('Hydrogen Exports'), 'Demand',
                        np.where(plot_data['Technology'].str.contains('FuelCell_h2_input'), 'Demand',
                                             None)))))))
plot_data['Type'] = np.where(plot_data['Technology'].str.contains('Total RE Generation'), 'RE',
                        np.where(plot_data['Technology'].str.contains('PowerPlant_Nuclear_existing_el_output'), 'Nuclear',
                        np.where(plot_data['Technology'].str.contains('Electrolyser_PEM_h2_output'), 'Onshore',
                        np.where(plot_data['Technology'].str.contains('Electrolyser_PEM_offshore_h2_output'), 'Offshore',
                        np.where(plot_data['Technology'].str.contains('hydrogen_input_gt'), 'Reconversion GT',
                        np.where(plot_data['Technology'].str.contains('FuelCell_h2_input'), 'Reconversion FC',
                        np.where(plot_data['Technology'].str.contains('Hydrogen Exports'), 'Direct Use',
                                             None)))))))
for case in plot_data['Subcase'].unique():
    st.markdown("**" + case + "**")

    plot_case = plot_data[(plot_data['Subcase'] == case)]

    chart = alt.Chart(plot_case).mark_bar().encode(
        x=alt.X('sum(value)'),
        color='Type',
        row=alt.Row('Side', title=None)
    ).interactive()

    st.altair_chart(chart)













def plot_layered_chart(plot_data, emission_target_selected, selected_case, deselected_cases, var_plot, title, legend_title_bar, legend_title_point='Other Scenarios'):
    all_charts = []

    max_value = max(plot_data[plot_data['Variable2'] == var_plot]['value']) * 1.1
    last_case = emission_target_selected[-1]
    first_case = emission_target_selected[0]

    for case in emission_target_selected:
        plot_data_case = plot_data[plot_data['Emission Reduction2'] == case]
        plot_data_selected_case = plot_data_case[plot_data_case['Subcase'].isin([selected_case])]
        plot_data_deselected_case = plot_data_case[plot_data_case['Subcase'].isin(deselected_cases)]

        if case == first_case:
            show_axis = True
            axis_orient = 'top'
            axis_title = title
        elif case == last_case:
            show_axis = True
            axis_orient = 'bottom'
            axis_title = None
        else:
            show_axis = False
            axis_orient = 'bottom'
            axis_title = None

        if legend_title_bar is None:
            legend_entry_bar = None
        else:
            legend_entry_bar = alt.Legend(title=legend_title_bar, orient='bottom')

        if legend_title_point is None:
            legend_entry_point = None
        else:
            legend_entry_point = alt.Legend(title=legend_title_point, orient='bottom')

        bar_size = alt.Chart(plot_data_selected_case[plot_data_selected_case['Variable2'] == var_plot]).mark_bar().encode(
            y=alt.Y('Variable2',
                    title = case,
                    axis=alt.Axis(labels=False)
                    ),
            x=alt.X('sum(value)',
                    title = axis_title,
                    axis=alt.Axis(labels=show_axis, orient=axis_orient),
                    scale=alt.Scale(domain=(0, max_value))
                    ),
            color = alt.Color('variable', legend=legend_entry_bar),
        )

        point_size = alt.Chart(plot_data_deselected_case[plot_data_deselected_case['Variable2'] == var_plot]).mark_point().encode(
            y=alt.Y('Variable2',
                    title = case,
                    axis=alt.Axis(labels=False)
                    ),
            x=alt.X('sum(value)'),
            shape=alt.Shape('Subcase', legend=legend_entry_point),
            color=alt.value('black')
        )

        chart_case = alt.layer(bar_size, point_size)
        all_charts.append(chart_case)

    return alt.vconcat(*all_charts)

# PLOT OVERVIEW
plot_data = summary_df[['Subcase',
                            'Emission Reduction2',
                            'abatemente_cost',
                            'Total Curtailment',
                            'Storage_Battery_new_size',
                            'Storage_Battery_Offshore_size',
                            'delta_emissions'
                         ]]

plot_data = plot_data.dropna(subset='Emission Reduction2').fillna(0)

# Select what to plot
st.header('The role of electricity storage')
st.subheader('Results for different scenarios and emission reduction targets')
st.markdown ('The plots below show emission reductions possible, abatement costs, required storage sizes (summed over'
             ' all nodes) and total curtailment for each case. To better compared scenarios, the other two scenarios'
             'are plotted in the same figures as black markers. If there is no entry shown, the respective emission'
             'reduction is infeasible with the selected scenario')

available_subcases = list(plot_data['Subcase'].unique())
emission_target = ['Min cost', '1%', '2%', '5%', '10%', '20%', '30%', '40%', '50%', 'Min emissions']
time_agg_options = {'Monthly Totals': 'Month',
                    'Weekly Totals': 'Week',
                    'Daily Totals': 'Day',
                    'Hourly Totals': 'Hour'}
spatial_agg_options = ['Country', 'Node']

with st.form('Results'):
    subcase_selected = st.selectbox('Select a scenario', available_subcases)
    emission_target_selected = st.multiselect('Select emission reduction targets to show', emission_target, default=emission_target)
    submitted = st.form_submit_button('Show')

    if submitted:
        plot_data = plot_data[plot_data['Emission Reduction2'].isin(emission_target_selected)]


        # Unit Conversion
        plot_data['Total Curtailment'] = plot_data['Total Curtailment']/1000000
        plot_data['Storage_Battery_new_size'] = plot_data['Storage_Battery_new_size']/1000
        plot_data['Storage_Battery_Offshore_size'] = plot_data['Storage_Battery_Offshore_size']/1000
        plot_data['delta_emissions'] = plot_data['delta_emissions']

        plot_data = plot_data.melt(id_vars=['Subcase', 'Emission Reduction2'])

        plot_data.loc[plot_data['variable'] == 'abatemente_cost', 'Variable2'] = 'abatemente_cost'
        plot_data.loc[plot_data['variable'] == 'Total Curtailment', 'Variable2'] = 'TotalCurtailment'
        plot_data.loc[plot_data['variable'] == 'Storage_Battery_new_size', 'Variable2'] = 'StorageSize'
        plot_data.loc[plot_data['variable'] == 'Storage_Battery_Offshore_size', 'Variable2'] = 'StorageSize'
        plot_data.loc[plot_data['variable'] == 'delta_emissions', 'Variable2'] = 'DeltaEmissions'

        plot_data['variable'] = plot_data['variable'].replace({'Storage_Battery_new_size': 'onshore'})
        plot_data['variable'] = plot_data['variable'].replace({'Storage_Battery_Offshore_size': 'offshore'})

        subcase_notselected = [n for n in available_subcases if n != subcase_selected]


        storage_size = plot_layered_chart(plot_data,
                                          emission_target_selected, subcase_selected, subcase_notselected,
                                          'StorageSize',
                                          'Storage Size (GWh)',
                                          'Storage Location', 'Other Scenarios')

        abatement_cost = plot_layered_chart(plot_data,
                                          emission_target_selected, subcase_selected, subcase_notselected,
                                          'abatemente_cost',
                                          'Abatement Costs (EUR/t)',
                                          None)

        emission_reduction = plot_layered_chart(plot_data,
                                          emission_target_selected, subcase_selected, subcase_notselected,
                                          'DeltaEmissions',
                                          'Emission Reduction compared to baseline (Mt)',
                                          None, 'Other Scenarios')

        curtailment = plot_layered_chart(plot_data,
                                          emission_target_selected, subcase_selected, subcase_notselected,
                                          'TotalCurtailment',
                                          'Total Curtailment (TWh)',
                                          None)

        first_row = alt.vconcat(emission_reduction, storage_size)
        second_row = alt.vconcat(abatement_cost, curtailment)

        chart_final = alt.hconcat(first_row, second_row)

        st.altair_chart(chart_final)

# OPERATION
st.subheader('Storage Operation')
st.markdown ('Select an emission reduction target and a scenario below to show the operation of the storage installed'
             'over time. You can also select a time aggregation')
with st.form('Operation'):
    subcase_selected = st.selectbox('Select a scenario', available_subcases, key='subcase_op')
    emission_target_selected = st.selectbox('Select emission reduction targets to show', emission_target,
                                            key='emission_op')
    st.markdown('Aggregation Options:')
    col1, col2 = st.columns([1, 1])
    with col1:
        time_agg = st.selectbox('Time Aggregation', time_agg_options.keys())
    with col2:
        spatial_agg = st.selectbox('Spatial Aggregation', spatial_agg_options)
    submitted = st.form_submit_button('Show')
    if submitted:
        load_path = summary_df[(summary_df['Case'] == 'Battery') &
                               (summary_df['Subcase'] == subcase_selected) &
                               (summary_df['Emission Reduction2'] == emission_target_selected)]['time_stamp'].values[0]

        # Load data
        with st.spinner('Wait for loading data...'):
            # Aggregate
            tec_operation = read_technology_operation(load_path + '/optimization_results.h5', re_gen_path)
            tec_design = read_technology_design(load_path + '/optimization_results.h5')


            tec_operation_agg_time_level = aggregate_time(tec_operation,
                time_agg_options[time_agg], aggregation='mean')
            tec_operation_agg_time_inout = aggregate_time(tec_operation,
                time_agg_options[time_agg])

            tec_operation_agg_level = aggregate_spatial_balance(tec_operation_agg_time_level, spatial_agg)
            tec_operation_agg_inout = aggregate_spatial_balance(tec_operation_agg_time_inout, spatial_agg)


        nodes =  tec_operation_agg_level.index.get_level_values('Node').unique()

        max_storage_size = tec_design[(tec_design['Technology'].isin(['Storage_Battery_new', 'Storage_Battery_Offshore'])) &
                                        (tec_design['Variable'].isin(['size']))].groupby('Technology').sum()
        max_storage_size = max_storage_size['Value'].sum()

        # Get input, output, level
        stor_level = tec_operation_agg_level.reset_index()
        stor_inout = tec_operation_agg_inout.reset_index()
        stor_level = stor_level[(stor_level['Technology'].isin(['Storage_Battery_new', 'Storage_Battery_Offshore'])) &
                                (stor_level['Variable'].isin(['storage_level']))].set_index(['Node', 'Technology', 'Carrier', 'Variable'])
        stor_input = stor_inout[(stor_inout['Technology'].isin(['Storage_Battery_new', 'Storage_Battery_Offshore'])) &
                                (stor_inout['Variable'].isin(['input']))].set_index(['Node', 'Technology', 'Carrier', 'Variable'])
        stor_output = stor_inout[(stor_inout['Technology'].isin(['Storage_Battery_new', 'Storage_Battery_Offshore'])) &
                                (stor_inout['Variable'].isin(['output']))].set_index(['Node', 'Technology', 'Carrier', 'Variable'])

        stor_output = stor_output * -1

        # Filter out zeros
        stor_level = stor_level.loc[(stor_level != 0).any(axis=1)]
        stor_input = stor_input.loc[(stor_input != 0).any(axis=1)]
        stor_output = stor_output.loc[(stor_output != 0).any(axis=1)]

        stor_level_melted = stor_level.reset_index().melt(id_vars=['Node', 'Technology', 'Carrier', 'Variable'])
        stor_input_melted = stor_input.reset_index().melt(id_vars=['Node', 'Technology', 'Carrier', 'Variable'])
        stor_output_melted = stor_output.reset_index().melt(id_vars=['Node', 'Technology', 'Carrier', 'Variable'])

        if len(stor_level_melted) >0:

            st.markdown('Select range:')
            # col1, col2 = st.columns([1,1])
            # with col1:
            min_value, max_value = st.slider('Min x-value',min(stor_level_melted['Timeslice']),  max(stor_level_melted['Timeslice']), (min(stor_level_melted['Timeslice']) , max(stor_level_melted['Timeslice'])))
            # with col2:
                # max_value = st.slider('Max x-value',min(stor_level_melted['Timeslice']) , max(stor_level_melted['Timeslice']))

            stor_level_melted = stor_level_melted[stor_level_melted['Timeslice'] >= min_value]
            stor_level_melted = stor_level_melted[stor_level_melted['Timeslice'] <= max_value]
            stor_output_melted = stor_output_melted[stor_output_melted['Timeslice'] >= min_value]
            stor_output_melted = stor_output_melted[stor_output_melted['Timeslice'] <= max_value]
            stor_input_melted = stor_input_melted[stor_input_melted['Timeslice'] >= min_value]
            stor_input_melted = stor_input_melted[stor_input_melted['Timeslice'] <= max_value]

            if max_value-min_value<=60:
                base_level = alt.Chart(stor_level_melted).mark_bar(width={'band': 0.5})
                base_input = alt.Chart(stor_input_melted).mark_bar(width={'band': 0.5})
                base_output = alt.Chart(stor_output_melted).mark_bar(width={'band': 0.5})
            else:
                base_level = alt.Chart(stor_level_melted).mark_area()
                base_input = alt.Chart(stor_input_melted).mark_area()
                base_output = alt.Chart(stor_output_melted).mark_area()

            area_level1 = base_level.encode(
                y=alt.Y('sum(value)',
                        title='Storage level (MWh)',
                        scale=alt.Scale(domain=(0, max_storage_size*1.1)),
                        ),
                x=alt.X('Timeslice:Q',
                        title=time_agg_options[time_agg],
                        scale=alt.Scale(domain=(min_value, max_value)),
                        axis=alt.Axis(format='d')
                        ),
                color=alt.Color('Node'),
            )

            area_level2 = alt.Chart(pd.DataFrame({'y': [max_storage_size]})).mark_rule(color='red').encode(
            y='y:Q'
            )

            area_level = area_level1 + area_level2

            area_output = base_input.encode(
                y=alt.Y('sum(value)',
                        title='Input/Output (MWh)'
                        ),
                x=alt.X('Timeslice:Q',
                        title=time_agg_options[time_agg],
                        scale=alt.Scale(domain=(min_value, max_value)),
                        axis=alt.Axis(format='d')
                        ),
                color=alt.Color('Node'),
            )

            area_input = base_output.encode(
                y=alt.Y('sum(value)',
                        title='Input/Output (MWh)'
                        ),
                x=alt.X('Timeslice:Q',
                        title=time_agg_options[time_agg],
                        scale=alt.Scale(domain=(min_value, max_value)),
                        axis=alt.Axis(format='d')
                        ),
                color=alt.Color('Node'),
            )

            st.altair_chart(area_level.properties(width=alt.Step(0)).interactive(), use_container_width=True)
            st.altair_chart((area_output + area_input).interactive(), use_container_width=True)
            # st.altair_chart(area_input, use_container_width=True)
        else:
            st.markdown('No storage installed in this scenario')



# OPERATION
st.subheader('Storage Location')
with st.form('Location'):
    subcase_selected = st.selectbox('Select a scenario', available_subcases, key='subcase_de')
    emission_target_selected = st.selectbox('Select emission reduction targets to show', emission_target, key='emission_de')
    submitted = st.form_submit_button('Show')
    if submitted:
        load_path = summary_df[(summary_df['Case'] == 'Battery') &
                               (summary_df['Subcase'] == subcase_selected) &
                               (summary_df['Emission Reduction2'] == emission_target_selected)]['time_stamp'].values[0]

        # Load data
        with st.spinner('Wait for loading data...'):
            # tec_design = read_technology_design('src/case_offshore_storage/visualization_v2/data/cases/BatteryAll_minemissions.h5')
            tec_design = read_technology_design(load_path + '/optimization_results.h5')

        storage_design = tec_design[(tec_design['Technology'].isin(['Storage_Battery_new', 'Storage_Battery_Offshore'])) &
                                    (tec_design['Variable'] == 'size')].groupby('Node').sum()
        storage_design['Value'] = storage_design['Value']/1000 # in TWh
        # st.table(storage_design)
        max_size = max(storage_design['Value'])

        fig, axis_positions, node_centroids, gs, axis = generate_map('Node', tec_design['Node'].unique())

        for node, row in storage_design.iterrows():
            if row['Technology'] == 'Storage_Battery_Offshore':
                y_start = axis_positions[node][0]
                y_end = axis_positions[node][1]+2
                x_start = axis_positions[node][2]+5
                x_end = axis_positions[node][3]
                ax_title = fig.add_subplot(gs[y_start,
                                          x_start-5:x_start + 4])
                ax_title.text(0, 0.5, node, horizontalalignment='left', verticalalignment='center', fontsize=4)
                ax_title.axis('off')
            else:
                y_start = axis_positions[node][0] + 3
                y_end = axis_positions[node][1]
                x_start = axis_positions[node][2]
                x_end = axis_positions[node][3]-4


            ax_storagesize = fig.add_subplot(gs[y_start:y_end-1,x_start+1:x_end - 1],
                                                frameon=True)

            ax_storagesize.barh(1, row['Value'], color='lightgreen')

            ax_storagesize.text(0.05, 1,
                    f"{row['Value']:.2f}",
                    ha='left', va='center', color='black', fontsize=4)

            ax_storagesize.set_xlim([0, max_size])
            ax_storagesize.axis('off')

        st.pyplot(fig)
