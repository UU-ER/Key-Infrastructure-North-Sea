import streamlit as st
import h5py
from utilities import *
import os

import altair as alt
import pandas as pd

st.header('Paper Title')

st.text('Introductory Text')


data = pd.read_excel(r'\\ad.geo.uu.nl\Users\StaffUsers\6574114\EhubResults\MES NorthSea\2040_demand_v6\Summary.xlsx')

st.table(data.melt(id_vars='time_stamp'))

chart = alt.Chart(data).mark_bar().encode(
    x=alt.X('total_costs'),
    y=alt.Y('net_emissions'),
).interactive()

st.altair_chart(chart)
