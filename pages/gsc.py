import streamlit as st
import pandas as pd
import plotly.express as px

df_full = pd.read_csv("data/full_matrix.csv")
df_priority = pd.read_csv("data/priority.csv")

df_priority['priority'] = df_priority['priority'].astype('boolean').fillna(False)

# df_full = df_full[df_full['TA_score'] > 40]

df_full = df_full.merge(df_priority, on='subcatg', how='left', suffixes=('', '_y'))
df_full['TA_score'] = df_full['TA_score'].astype(float)
df_full['priority'] = df_full['priority'].astype(bool)

treemap_colors = {
    "treemap_good": "#059669",
    "treemap_middle": "#c5cfc4",
    "treemap_bad": "#ef4444",
}

def treemap(selected_value, df, selected_metric):
    metric_mapping = {
        "Position": "position",
        "CTR": "ctr", 
        "Impressions": "impressions"
    }
    
    size_col_name = metric_mapping[selected_metric]
    
    data_filtered = df.where(
        (df[size_col_name] >= selected_value[0]) & (df[size_col_name] <= selected_value[1])
    ).dropna()

    fig = px.treemap(
        data_filtered, 
        path=['catg', 'subcatg', 'query'], 
        values='impressions',
        color=size_col_name,
        color_continuous_scale=[
            treemap_colors['treemap_good'], 
            treemap_colors['treemap_middle'], 
            treemap_colors['treemap_bad']
        ],
        title=f"Treemap filtrado por {selected_metric}"
    )
    fig.update_traces(marker=dict(cornerradius=5), root_color="lightgrey")
    
    return fig

st.title("GSC Trends Treemap")

# Checkbox para mostrar solo subcategorías priorizadas
show_priority_only = st.checkbox("Mostrar solo subcategorías priorizadas", value=False)

# Filtrar datos según la selección del checkbox
if show_priority_only:
    df_filtered = df_full[(df_full['priority'].notna()) & (df_full['priority'] == True)]
else:
    df_filtered = df_full

# Forzar refresco cuando cambie el checkbox
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

current_column = metric_mapping[selected_metric]

if selected_metric == "CTR":
    step_size = 0.01
    format_str = "%.2f"
    min_val = float(df_filtered[current_column].min())
    max_val = float(df_filtered[current_column].max())
    default_min = min_val
    default_max = max_val
else:
    step_size = 1
    format_str = "%d"
    min_val = int(df_filtered[current_column].min())
    max_val = int(df_filtered[current_column].max())
    default_min = min_val
    default_max = max_val

with col2:
    selected_value = st.slider(
        f"Rango de {selected_metric}",
        min_value=min_val,
        max_value=max_val,
        value=(default_min, default_max),
        step=step_size,
        format=format_str,
        key=f"slider_{show_priority_only}_{selected_metric}"
    )

st.info(f"Filtrando por {selected_metric}: {selected_value[0]} - {selected_value[1]}")

fig = treemap(selected_value, df_filtered, selected_metric)
st.plotly_chart(fig, use_container_width=True)