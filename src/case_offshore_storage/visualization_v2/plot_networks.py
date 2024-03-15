from folium.features import DivIcon
import folium
from branca.colormap import linear
from folium.plugins import PolyLineTextPath, PolyLineOffset
from utilities import *

def plot_nodes_centroids(map, node_data):
    for node_name, data in node_data.iterrows():
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=5,  # Adjust the radius as needed
            color='black',  # Marker color
            fill=True,
            fill_color='black',  # Fill color
            fill_opacity=0.7,
        ).add_to(map)
        folium.map.Marker(
            [data['lat'], data['lon']],
            icon=DivIcon(icon_size=(150, 36),
                         icon_anchor=(-5, 20),
                         html='<div style="font-size: 9pt">' + node_name + '</div>')
        ).add_to(map)



def plot_network(h5_path, networks_to_plot, selected_var):

    # Read Data
    node_data = pd.read_csv('./src/case_offshore_storage/visualization_v2/data/Node_Locations.csv', sep=';', index_col=0)
    with h5py.File(h5_path, 'r') as hdf_file:
        network_design = extract_datasets_from_h5_group(hdf_file["design/networks"])

    network_design = network_design.melt()
    network_design.columns = ['Network', 'Arc_ID', 'Variable', 'Value']
    network_design = network_design.pivot(columns='Variable', index=['Arc_ID', 'Network'], values='Value')
    network_design['FromNode'] = network_design['fromNode'].str.decode('utf-8')
    network_design['ToNode'] = network_design['toNode'].str.decode('utf-8')
    network_design.drop(columns=['fromNode', 'toNode', 'network'], inplace=True)
    network_design = network_design.reset_index()

    # Select a network
    network_df_filtered = network_design[network_design['Network'].isin(networks_to_plot)]

    arc_ids = network_df_filtered[['Arc_ID', 'FromNode', 'ToNode']]
    network_df_filtered = network_df_filtered.groupby('Arc_ID').sum()
    network_df_filtered.drop(columns=['FromNode', 'ToNode', 'Network'], inplace=True)
    network_df_filtered = network_df_filtered.merge(arc_ids, on='Arc_ID')

    # Initialize Map
    map_center = [node_data['lat'].mean(), node_data['lon'].mean()]
    map = folium.Map(location=map_center, zoom_start=5)

    # Plot Nodes
    plot_nodes_centroids(map, node_data)

    # Plot edges
    variables = {'Network Size': 'size', 'Total Flow': 'total_flow'}

    if len(network_df_filtered) > 0:

        max_value = max(network_df_filtered[variables[selected_var]])
        color_scale = linear.OrRd_09.scale(0, 1)

        for _, edge_data in network_df_filtered.iterrows():
            from_node_data = node_data.loc[edge_data.FromNode]
            to_node_data = node_data.loc[edge_data.ToNode]

            # Normalize edge value to be within [0, 1]
            normalized_value = (edge_data[variables[selected_var]]) / max_value
            # Determine color based on the color scale
            color = color_scale(normalized_value)
            if normalized_value > 0.001:
                if selected_var == 'Network Size':
                    unit = 'GW'
                    f = folium.PolyLine
                else:
                    unit = 'GWh'
                    f = folium.plugins.PolyLineOffset
                line = f([(from_node_data['lat'], from_node_data['lon']),
                                                    (to_node_data['lat'], to_node_data['lon'])],
                                                     color=color,
                                                     weight=6,  # Set a default weight
                                                     opacity=1,
                                                     offset=5,
                                                     tooltip=selected_var + ': ' + str(
                                                         round(edge_data[variables[selected_var]] / 1000,
                                                               1)) + unit).add_to(map)
                attr = {"font-weight": "bold", "font-size": "13"}

                if selected_var != 'Network Size':
                    folium.plugins.PolyLineTextPath(
                        line, "      >", repeat=True, offset=5, attributes=attr
                    ).add_to(map)

    return map
