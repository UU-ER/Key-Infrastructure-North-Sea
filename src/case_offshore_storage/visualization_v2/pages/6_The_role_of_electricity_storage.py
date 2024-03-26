import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path
import folium
from streamlit_folium import st_folium
import h5py

from plot_networks import *
from utilities import *
from read_data import *

st.set_page_config(layout="wide")

# Data required
root = 'src/case_offshore_storage/visualization_v2/'
re_gen_path = root + 'data/production_profiles_re.csv'
result_path = root + 'data/cases/'
case_keys = root + 'data/Cases.csv'
cases_available = pd.read_csv(case_keys, sep=';')

summary_df = pd.read_excel('./src/case_offshore_storage/visualization_v2/data/Summary_Plotting6_processed.xlsx')
summary_df = summary_df[summary_df['Case'] == 'Battery']


def plot_layered_chart(plot_data, emission_target_selected, selected_case, deselected_cases, var_plot, title, legend_title_bar, legend_title_point='Other Scenarios'):
    all_charts = []

    max_value = max(plot_data[plot_data['Variable2'] == var_plot]['value']) * 1.1
    last_case = emission_target_selected[-1]
    first_case = emission_target_selected[0]

    for case in emission_target_selected:
        plot_data_case = plot_data[plot_data['Emission Reduction'] == case]
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
                            'Emission Reduction',
                            'abatemente_cost',
                            'Total Curtailment',
                            'Storage_Battery_new_size',
                            'Storage_Battery_Offshore_size',
                            'delta_emissions'
                         ]]

plot_data = plot_data.dropna(subset='Emission Reduction').fillna(0)

# Select what to plot
st.header('The role of electricity storage')
st.subheader('Results for different scenarios and emission reduction targets')
st.markdown ('The plots below show emission reductions possible, abatement costs, required storage sizes (summed over'
             ' all nodes) and total curtailment for each case. To better compared scenarios, the other two scenarios'
             'are plotted in the same figures as black markers. If there is no entry shown, the respective emission'
             'reduction is infeasible with the selected scenario')

available_subcases = list(plot_data['Subcase'].unique())
subcase_selected = st.selectbox('Select a scenario', available_subcases)

emission_target = ['Min cost', '1%', '2%', '5%', '10%', '20%', '30%', '40%', '50%', 'Min emissions']
emission_target_selected = st.multiselect('Select emission reduction targets to show', emission_target, default=emission_target)

plot_data = plot_data[plot_data['Emission Reduction'].isin(emission_target_selected)]

# Unit Conversion
plot_data['Total Curtailment'] = plot_data['Total Curtailment']/1000000
plot_data['Storage_Battery_new_size'] = plot_data['Storage_Battery_new_size']/1000
plot_data['Storage_Battery_Offshore_size'] = plot_data['Storage_Battery_Offshore_size']/1000
plot_data['delta_emissions'] = plot_data['delta_emissions']/1000000

plot_data = plot_data.melt(id_vars=['Subcase', 'Emission Reduction'])

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


subcase_selected = st.selectbox('Select a scenario', available_subcases, key='subcase_op')
emission_target_selected = st.selectbox('Select emission reduction targets to show', emission_target, key='emission_op')

st.markdown('Aggregation Options:')
col1, col2 = st.columns([1,1])
with col1:
    time_agg_options = {'Monthly Totals': 'Month',
                        'Weekly Totals': 'Week',
                        'Daily Totals': 'Day',
                        'Hourly Totals': 'Hour'}
    time_agg = st.selectbox('Time Aggregation', time_agg_options.keys())
with col2:
    spatial_agg_options = ['Country', 'Node']
    spatial_agg = st.selectbox('Spatial Aggregation', spatial_agg_options)

load_path = summary_df[(summary_df['Case'] == 'Battery') &
                       (summary_df['Subcase'] == subcase_selected) &
                       (summary_df['Emission Reduction'] == emission_target_selected)]['time_stamp'].values[0]

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

    if max_value-min_value<=70:
        base_level = alt.Chart(stor_level_melted).mark_bar(width={'band': 1})
        base_input = alt.Chart(stor_input_melted).mark_bar(width={'band': 1})
        base_output = alt.Chart(stor_output_melted).mark_bar(width={'band': 1})
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