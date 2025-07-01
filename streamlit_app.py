import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.preprocessing import MinMaxScaler

df_full = pd.read_csv("data/grouped_matrix.csv")
df_priority = pd.read_csv("data/priority.csv")

df_full['priority'] = df_full['priority'].fillna(False)
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

st.title("Entities Trends Treemap")

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
