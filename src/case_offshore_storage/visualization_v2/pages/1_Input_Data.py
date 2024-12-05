import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

re_profiles = pd.read_csv('C:/Users/6574114/Documents/Research/EHUB-Py_Productive/input_data/clean_data/production_profiles_re/production_profiles_re.csv',
                          header=[0,1])
filtered_df = re_profiles.loc[:, re_profiles.columns.get_level_values(1) == 'total']

# st.text(filtered_re_profiles)

# Calculate correlation matrix
# Calculate correlation matrix
corr = filtered_df.corr()

# Create correlation plot using seaborn
fig = plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=False, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Correlation Plot for Columns with Label "Total"')
plt.show()

st.pyplot(fig)
