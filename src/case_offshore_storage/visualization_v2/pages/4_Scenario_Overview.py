import pandas as pd
import altair as alt
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def frame_around_fig(ax, show_frame=True):
    ax.set_frame_on(show_frame)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])


# Read data
all_cases = pd.read_excel('src/case_offshore_storage/visualization_v2/data/Summary_Plotting.xlsx')
all_cases = all_cases[(all_cases['Case'] != 'Baseline')].dropna(subset=['Emission Reduction'])
max_reduction = all_cases[all_cases['Emission Reduction'] == 'Min emissions']
max_abatement = all_cases['abatemente_cost'].max()
min_abatement = all_cases['abatemente_cost'].min()

# Filter data
all_cases = all_cases[(all_cases['Case'] != 'Baseline') & (all_cases['Emission Reduction'] != 'Min emissions')]

# all_case_pos = all_cases[all_cases['abatemente_cost'] >= 0]
# all_case_neg = all_cases[all_cases['abatemente_cost'] <= 0]
# all_case_neg['abatemente_cost'] = all_case_neg['abatemente_cost'] * -1

# Plot the bars for each case
sort_cases = ['50%', '40%', '30%', '20%', '10%', '5%', '2%', '1%', 'Min cost']
fig = plt.figure()
fig.subplots_adjust(hspace=0, wspace=0, left=0, right=1, top=1, bottom=0)
gs = fig.add_gridspec(len(all_cases)+1, 5, width_ratios=[2, 4, 4, 2, 4])

x_tick_markers_pos_at = [100, 1000, 10000]
x_tick_markers_neg_at = [-100, -50, 0]

#
ax_background = fig.add_subplot(gs[0:len(all_cases)+1, 0:5], frameon=True)
frame_around_fig(ax_background, show_frame=True)
ax_background.axvline(x=12/16, color='red', linestyle='--')

# Top plots
ax_axis_neg = fig.add_subplot(gs[0, 3], frameon=True)
ax_axis_neg.set_xlim(min_abatement * 1.1, 0)
ax_axis_neg.set_ylim(-1, 0)
ax_axis_neg.grid(False)
ax_axis_neg.set_yticks([])
ax_axis_neg.set_frame_on(False)
ax_axis_neg.xaxis.tick_top()
ax_axis_neg.set_xticks(x_tick_markers_neg_at)
for tick in x_tick_markers_neg_at:
    if tick != 0:
        ax_axis_neg.axvline(x=tick, color='black')
    # else:
    #     ax_axis_neg.axvline(x=tick, color='red')

ax_axis_pos = fig.add_subplot(gs[0, 4], frameon=True)
ax_axis_pos.set_xscale('log')
ax_axis_pos.set_xlim(1, max_abatement * 1.1)
# ax_axis_pos.set_ylim(-1, 0)
ax_axis_pos.grid(False)
ax_axis_pos.set_yticks([])
ax_axis_pos.set_frame_on(False)
ax_axis_pos.xaxis.tick_top()
ax_axis_pos.set_xticks(x_tick_markers_pos_at)
for tick in x_tick_markers_pos_at:
    ax_axis_pos.axvline(x=tick, color='black')


idx = 1
for emission_red_case in sort_cases:
    plot_data = all_cases[all_cases['Emission Reduction'] == emission_red_case]
    len_reduction = len(plot_data)
    ax_reduction = fig.add_subplot(gs[idx:idx + len_reduction, 0], frameon=True)
    ax_reduction.text(0.05, 0.5, emission_red_case, verticalalignment='center')
    frame_around_fig(ax_reduction, show_frame=True)


    cases = plot_data['Case'].unique()
    idx_case = idx

    for case in cases:
        plot_data_case = plot_data[plot_data['Case'] == case]
        len_cases = len(plot_data_case)

        ax_case = fig.add_subplot(gs[idx_case:idx_case+len_cases,1], frameon=True)
        ax_case.text(0.05, 0.5, case, verticalalignment='center')
        frame_around_fig(ax_case, show_frame=True)

        idx_subcase = idx_case
        for subcase in plot_data_case['Subcase']:
            plot_data_sub_case = plot_data_case[plot_data_case['Subcase'] == subcase]

            ax_subcase_title = fig.add_subplot(gs[idx_subcase,2], frameon=True)
            ax_subcase_title.text(0.05, 0.5, subcase, verticalalignment='center')
            frame_around_fig(ax_subcase_title, show_frame=False)

            # Positive Values
            ax_subcase_pos = fig.add_subplot(gs[idx_subcase,4], frameon=True)
            if plot_data_sub_case['abatemente_cost'].values[0] > 0:
                ax_subcase_pos.barh(plot_data_sub_case['Subcase'], plot_data_sub_case['abatemente_cost'])
            ax_subcase_pos.text(0, 0.5, str(round(plot_data_sub_case['abatemente_cost'].values[0],1)), ha='left', va='center',transform=ax_subcase_pos.transAxes)
            ax_subcase_pos.set_xscale('log')
            ax_subcase_pos.set_xlim(1, max_abatement*1.1)
            for tick in x_tick_markers_pos_at:
                ax_subcase_pos.axvline(x=tick, color='black')
            frame_around_fig(ax_subcase_pos, show_frame=False)

            # Negative Values
            ax_subcase_neg = fig.add_subplot(gs[idx_subcase,3], frameon=True)
            if plot_data_sub_case['abatemente_cost'].values[0] < 0:
                ax_subcase_neg.barh(plot_data_sub_case['Subcase'], plot_data_sub_case['abatemente_cost'])
            frame_around_fig(ax_subcase_neg, show_frame=False)
            ax_subcase_neg.set_xlim(min_abatement * 1.1, 0)
            for tick in x_tick_markers_neg_at:
                if tick != 0:
                    ax_subcase_neg.axvline(x=tick, color='black')


            idx_subcase += 1

        idx_case = idx_case + len_cases
    #
    # ax.barh(plot_data['Subcase'], plot_data['abatemente_cost'])
    #
    # ax.set_title(emission_red_case)
    idx = idx + len_reduction


#
# for i, (name, group) in enumerate(grouped_data):
#     pass
#     # plt.barh([pos + i * bar_width for pos in bar_positions], group['abatement_cost'], height=bar_width, label=name)
#
# # Add labels and legend
# plt.xlabel('Abatement Cost')
# plt.ylabel('Subcase')
# plt.yticks([pos + bar_width for pos in bar_positions], categories)
# plt.legend(title='Case')

st.pyplot(fig)










for case in sort_cases:
    plot_case = all_cases[(all_cases['Emission Reduction'] == case)]

    # Positive Emissions
    chart_pos = alt.Chart(plot_case).mark_bar().encode(
        x=alt.X('abatemente_cost', scale=alt.Scale(zero=True, domainMax=max_abatement), title=None),
        y=alt.Y('Subcase', title=None, sort='descending'),
        color = 'Case',
        row=alt.Row('Case', title=case + ' reduction')
    ).interactive()
    #
    # chart_neg =
    #
    # text = chart_pos.mark_text(
    #     align='left',
    #     baseline='middle',
    #     dx=3  # Nudges text to right so it doesn't appear on top of the bar
    # ).encode(
    #     text='abatemente_cost:Q'
    # )

    # ).encode(
    #
    # )
    # # Text
    # text = chart_pos.mark_text(
    #     align='left',
    #     baseline='middle',
    #     dx=3  # Adjust this value as needed to position the text properly
    # )

    # alt.layer(chart_pos + text)
    st.altair_chart(chart_pos)

#
# chart_neg = alt.Chart(all_case_neg).mark_bar().encode(
#     x=alt.X('abatemente_cost').scale(type="log"),
#     y='Case',
#     color='Case',
#     row='Emission Reduction'
# )
#
# st.altair_chart(chart_neg)
#
# # chart_energy = alt.Chart(
# #     st.session_state['line_data_energy'].reset_index().melt(id_vars=['index'])).mark_line().encode(
# #     x=alt.X('Timeslice:Q', axis=alt.Axis(format='d')).title(time_agg_options[time_agg]),
# #     y=alt.Y('value').title('Energy (MWh)', titleColor='#57A44C'),
# #     color='index',
# #     tooltip=['Timeslice', 'value']
# # ).properties(
# #     width=800,
# #     height=400
# # ).interactive()

# st.text(all_case_pos)
#


