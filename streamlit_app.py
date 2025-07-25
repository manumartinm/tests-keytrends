import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler

st.title("Entities Trends Treemap")

data_folder = "data"
subfolders = [f.name for f in os.scandir(data_folder) if f.is_dir()]

if not subfolders:
    st.error("No hay subcarpetas dentro de la carpeta 'data'.")
    st.stop()

selected_subfolder = st.selectbox("Selecciona una carpeta de datos:", subfolders, index=0)

# Construir rutas a los CSV dentro de la carpeta seleccionada
folder_path = os.path.join(data_folder, selected_subfolder)
full_matrix_path = os.path.join(folder_path, "grouped_matrix.csv")
priority_path = os.path.join(folder_path, "priority.csv")

try:
    df_full = pd.read_csv(full_matrix_path, sep=',', encoding='utf-8')
    df_priority = pd.read_csv(priority_path)
except FileNotFoundError:
    st.error("No se encontraron los archivos CSV requeridos en la carpeta seleccionada.")
    st.stop()

df_priority['priority'] = df_priority['priority'].astype('boolean').fillna(False)

agg_column = 'count'
agg_func = 'sum'

df_grouped = (
    df_full
    .groupby(['catg', 'subcatg', 'entity'], as_index=False)
    .agg({agg_column: agg_func, 'TA_score': 'mean'})  # promedio de TA_score si varía entre queries
)

df_grouped['count_log'] = np.log1p(df_grouped[agg_column])
epsilon = 1e-6
df_grouped['count_scaled'] = MinMaxScaler().fit_transform(df_grouped[['count_log']]) + epsilon

df_grouped = df_grouped.merge(df_priority, on='subcatg', how='left', suffixes=('', '_y'))
df_grouped['priority'] = df_grouped['priority'].fillna(False)
df_grouped['priority'] = df_grouped['priority'].astype(bool)

treemap_colors = {
    "treemap_good": "#059669",
    "treemap_middle": "#c5cfc4",
    "treemap_bad": "#ef4444",
}


def treemap(selected_value, df):
    size_col_name = 'TA_score'

    data_filtered = df[
        (df['TA_score'] >= selected_value[0]) &
        (df['TA_score'] <= selected_value[1]) &
        (df['count_scaled'] > 0)
    ]

    fig = px.treemap(
        data_filtered,
        path=['catg', 'subcatg', 'entity'],
        values='count_scaled',
        color=size_col_name,
        color_continuous_scale=[
            treemap_colors['treemap_bad'],
            treemap_colors['treemap_middle'],
            treemap_colors['treemap_good'],
        ],
    )
    fig.update_traces(marker=dict(cornerradius=5), root_color="lightgrey")
    return fig


show_priority_only = st.checkbox("Mostrar solo subcategorías priorizadas", value=False)

df_filtered = (
    df_grouped[df_grouped['priority']] if show_priority_only
    else df_grouped
)

if df_filtered.empty:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
    st.stop()

selected_value = st.slider(
    "Select Topical Authority Range",
    min_value=float(df_filtered['TA_score'].min()),
    max_value=float(df_filtered['TA_score'].max()),
    value=(float(df_filtered['TA_score'].min()), float(df_filtered['TA_score'].max())),
    key=f"slider_{show_priority_only}"
)

# Mostrar gráfico
fig = treemap(selected_value, df_filtered)
st.plotly_chart(fig, use_container_width=True)
