import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

st.title("GSC Trends Treemap")

data_folder = "data"
subfolders = [f.name for f in os.scandir(data_folder) if f.is_dir()]

if not subfolders:
    st.error("No hay subcarpetas dentro de la carpeta 'data'.")
    st.stop()

selected_subfolder = st.selectbox("Selecciona una carpeta de datos:", subfolders, index=0)

# Construir rutas a los CSV dentro de la carpeta seleccionada
folder_path = os.path.join(data_folder, selected_subfolder)
full_matrix_path = os.path.join(folder_path, "full_matrix.csv")
priority_path = os.path.join(folder_path, "priority.csv")

try:
    df_full = pd.read_csv(full_matrix_path, sep=',', encoding='utf-8')
    df_priority = pd.read_csv(priority_path)
except FileNotFoundError:
    st.error("No se encontraron los archivos CSV requeridos en la carpeta seleccionada.")
    st.stop()

df_priority['priority'] = df_priority['priority'].astype('boolean').fillna(False)

df_full = df_full.merge(df_priority, on='subcatg', how='left', suffixes=('', '_y'))
df_full['TA_score'] = df_full['TA_score'].astype(float)
df_full['priority'] = df_full['priority'].fillna(False)

treemap_colors = {
    "treemap_good": "#059669",
    "treemap_middle": "#c5cfc4",
    "treemap_bad": "#ef4444",
}

show_priority_only = st.checkbox("Mostrar solo subcategorías priorizadas", value=False)

df_filtered = df_full[df_full['priority']] if show_priority_only else df_full.copy()

if df_filtered.empty:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
    st.stop()

col1, col2 = st.columns([1, 2])
with col1:
    selected_metric = st.selectbox(
        "Seleccionar métrica para filtrar:",
        ["Position", "CTR", "Impressions"],
        index=0,
        key=f"metric_{show_priority_only}"
    )

metric_mapping = {
    "Position": "position",
    "CTR": "ctr", 
    "Impressions": "impressions"
}
metric_column = metric_mapping[selected_metric]

if selected_metric == "CTR":
    step_size = 0.01
    format_str = "%.2f"
    min_val = float(df_filtered[metric_column].min())
    max_val = float(df_filtered[metric_column].max())
else:
    step_size = 1
    format_str = "%d"
    min_val = int(df_filtered[metric_column].min())
    max_val = int(df_filtered[metric_column].max())

with col2:
    selected_value = st.slider(
        f"Rango de {selected_metric}",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        step=step_size,
        format=format_str,
        key=f"slider_{show_priority_only}_{selected_metric}"
    )

df_grouped = (
    df_filtered
    .groupby(['catg', 'subcatg', 'query'], as_index=False)
    .agg({
        metric_column: 'mean',
        'TA_score': 'mean'
    })
)

df_grouped['metric_log'] = np.log1p(df_grouped[metric_column])
df_grouped['metric_scaled'] = (
    MinMaxScaler().fit_transform(df_grouped[['metric_log']]) + 1e-6
)

df_grouped = df_grouped[
    (df_grouped[metric_column] >= selected_value[0]) &
    (df_grouped[metric_column] <= selected_value[1])
]

if df_grouped.empty:
    st.warning("No hay datos que cumplan los filtros.")
    st.stop()

if selected_metric == "Position":
    colors = [
        treemap_colors['treemap_good'],
        treemap_colors['treemap_middle'],
        treemap_colors['treemap_bad'],
    ]
else:
    colors = [
        treemap_colors['treemap_bad'],
        treemap_colors['treemap_middle'],
        treemap_colors['treemap_good'],
    ]

fig = px.treemap(
    df_grouped,
    path=['catg', 'subcatg', 'query'],
    values='metric_scaled',
    color=metric_column,
    color_continuous_scale=colors,
    title=f"Treemap filtrado por {selected_metric}"
)
fig.update_traces(marker=dict(cornerradius=5), root_color="lightgrey")

st.info(f"Filtrando por {selected_metric}: {selected_value[0]} - {selected_value[1]}")
st.plotly_chart(fig, use_container_width=True)
