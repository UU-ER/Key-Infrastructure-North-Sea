import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path
import folium
from streamlit_folium import st_folium
import h5py

from plot_networks import *
from utilities import *

st.set_page_config(layout="wide")

# Data required
root = 'src/case_offshore_storage/visualization_v2/'
result_path = root + 'data/cases/'
case_keys = root + 'data/Cases.csv'
cases_available = pd.read_csv(case_keys, sep=';')

# Starting Grid
st.header('The role of electricity grids')
st.markdown ('Compared to the baseline, electricity grids can be expanded along existing and new corridors '
        'shown in the figure below. On the bottom of the page you can visualize the results of the optimizations'
        'for three different scenarios.')

st.subheader('The starting grid and possible expansion corridors')
st.markdown('Compared to the baseline, electricity grids can be expanded along existing and new corridors '
        'shown in the figure below. Select an item from the list below do get an understanding of the '
        'underlying grid assumptions. You can hoover over a line to see its capacity.' )

grid_type_to_show = st.selectbox('Select existing or expansion corridors', ['Starting grid',
                                                                            'Expansion corridors'])

grids_to_show = st.selectbox('Select networks to show', ['AC and DC grid (combined)',
                                                         'AC grid',
                                                         'DC grid'
                                                         ])

h5_path = result_path + cases_available[cases_available['case'].str.contains('Baseline', regex=False)]['file_name'].values[0]

if grids_to_show == 'AC grid':
    selected_networks = ['electricityAC_existing']
elif grids_to_show == 'DC grid':
    selected_networks = ['electricityDC_existing']
elif grids_to_show == 'AC and DC grid (combined)':
    selected_networks = ['electricityAC_existing', 'electricityDC_existing']

map_existing_networks = plot_network(h5_path,selected_networks,'Network Size')
st_folium(map_existing_networks, width=900)

# Scenario Results
st.subheader('Results for different scenarios')

summary_df = pd.read_excel('./src/case_offshore_storage/visualization_v2/data/Summary_Plotting2.xlsx')
summary_df = summary_df[['Case',
                            'Subcase',
                            'Emission Reduction',
                            'delta_cost',
                            'delta_emissions',
                            'abatemente_cost',
                            'Carbon Costs',
                            'Electricity Import Costs',
                            'Hydrogen Export Revenues',
                            'Network Costs (existing)',
                            'Network Costs (new)',
                            'Technology Costs (existing)',
                            'Technology Costs (new)',
                            'Total Curtailment',
                            'Total RE Generation'
                         ]]

summary_df['Curtailment Fraction'] = summary_df['Total Curtailment'] / (summary_df['Total Curtailment'] + summary_df['Total RE Generation'])

summary_df_all = (summary_df[(summary_df['Case'].isin(['Baseline', 'Grid Expansion'])) & (summary_df['Emission Reduction'] == 'Min cost')].
                       set_index(['Case', 'Subcase', 'Emission Reduction']))
summary_df_baseline = (summary_df[(summary_df['Case'].isin(['Baseline'])) & (summary_df['Emission Reduction'] == 'Min cost')].
                       set_index(['Case', 'Subcase', 'Emission Reduction']))
summary_df_grid = (summary_df[(summary_df['Case'].isin(['Grid Expansion'])) & (summary_df['Emission Reduction'] == 'Min cost')].
                   set_index(['Case', 'Subcase', 'Emission Reduction']))


# COSTS
cost_diff = summary_df_grid[['delta_cost',
                             'Carbon Costs',
                            'Electricity Import Costs',
                            'Hydrogen Export Revenues',
                            'Network Costs (existing)',
                            'Network Costs (new)',
                            'Technology Costs (existing)',
                            'Technology Costs (new)']].subtract(summary_df_baseline[['delta_cost',
                            'Carbon Costs',
                            'Electricity Import Costs',
                            'Hydrogen Export Revenues',
                            'Network Costs (existing)',
                            'Network Costs (new)',
                            'Technology Costs (existing)',
                            'Technology Costs (new)']].iloc[0])

cost_diff['delta_cost'] = - cost_diff['delta_cost']
cost_diff['Total net savings'] = cost_diff['delta_cost']
cost_diff['Network Costs (new)'] = - cost_diff['Network Costs (new)']

cost_diff_melted = cost_diff.reset_index().drop(columns=['Emission Reduction']).melt(id_vars = ['Case', 'Subcase'])
cost_diff_melted['Category'] = 'Savings'
cost_diff_melted.loc[cost_diff_melted['variable'].isin(['Network Costs (new)', 'delta_cost']), 'Category'] = 'Additional Costs'
cost_diff_melted.loc[cost_diff_melted['variable'].isin(['Total net savings']), 'Category'] = 'Total net savings'
cost_diff_melted['value'] = cost_diff_melted['value'] /1000000

cost_diff_melted = cost_diff_melted[cost_diff_melted['variable'].isin(['Network Costs (new)',
                                                                       'Carbon Costs',
                                                                       'Network Costs (new)',
                                                                       'Total net savings',
                                                                       'Technology Costs (existing)',
                                                                       'delta_cost'])]


colors = {'delta_cost': '#ff7f0e00',
'Carbon Costs': '#1f77b4',
 'Network Costs (new)': '#ff7f0e',
 'Technology Costs (existing)': '#aec7e8',
 'Total net savings': '#98df8a'}

chart_cost = alt.Chart(cost_diff_melted).mark_bar().encode(
    x=alt.X('sum(value)', title='mio EUR'),
    y=alt.Y('Category', sort=['Savings', 'Additional Costs', 'Total net Savings'], title = None),
    row=alt.Row('Subcase', sort=['all', 'onshore only', 'no border cross', 'offshore only'], title =None),
    color=alt.Color('variable',
                    scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())),
                    legend=alt.Legend(values=['Carbon Costs', 'Network Costs (new)', 'Technology Costs (existing)'])),
    order = alt.Order(sort='descending')
    )

# CURTAILMENT
curtailment_melted = summary_df_all[['Curtailment Fraction']].reset_index().drop(columns=['Emission Reduction']).melt(id_vars = ['Case', 'Subcase'])
chart_curtailment = alt.Chart(curtailment_melted).mark_bar().encode(
    x=alt.X('sum(value)', title='Curtailment (% of total available renewable generation)').axis(format='%'),
    y=alt.Y('Subcase', title = None, sort=['Baseline', 'all', 'onshore only', 'no border cross', 'offshore only']),
    color=alt.Color('Case', legend=None)
    )

curtailment_text = chart_curtailment.mark_text(
    align='left',
    baseline='middle',
    dx=3
).encode(
    text=alt.Text('value:Q', format='.2%')
)


# EMISSIONS
emissions_melted = summary_df_all[['delta_emissions']].reset_index().drop(columns=['Emission Reduction']).melt(id_vars = ['Case', 'Subcase'])
emissions_melted['value'] = -emissions_melted['value']/1000
emissions_melted = emissions_melted[emissions_melted['Case'] != 'Baseline']
chart_emissions = alt.Chart(emissions_melted).mark_bar().encode(
    x=alt.X('sum(value)', title='Emission Reduction compared to baseline (Mt)'),
    y=alt.Y('Subcase', title = None, sort=['all', 'onshore only', 'no border cross', 'offshore only'])
)

emissions_text = chart_emissions.mark_text(
    align='right',
    baseline='middle',
    dx=-3
).encode(
    text=alt.Text('value:Q', format='.1f')
)

st.markdown('**Changes in total system costs**')
st.altair_chart(chart_cost.properties(width=500).interactive())
st.markdown('**Curtailment**')
st.altair_chart((curtailment_text + chart_curtailment).properties(width=500).interactive())
st.markdown('**Emission Reduction**')
st.altair_chart((emissions_text + chart_emissions).properties( width=500).interactive())

# EXPANSION CORRIDORS
st.markdown('**Expansion Corridors used in specific scenarios**')

case_selected = st.selectbox('Select a scenario to show the expansion corridors used on a map', ['Grid Expansion (all)',
                                           'Grid Expansion (onshore only)',
                                           'Grid Expansion (offshore only)',
                                           'Grid Expansion (no border cross)'])
vars_available = ['Network Size', 'Total Flow']
selected_var = st.selectbox('Select a variable to show:', vars_available)

st.markdown('You can hoover over a line to see its annual flow/ its capacity')

h5_path = result_path + cases_available[cases_available['case'].str.contains(case_selected, regex=False)]['file_name'].values[0]
map_new_networks = plot_network(h5_path, ['electricityDC', 'electricityAC'], selected_var)
st_folium(map_new_networks, width=900)