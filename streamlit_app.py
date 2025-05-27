import streamlit as st
import pandas as pd
import plotly.express as px

df_full = pd.read_csv("data/grouped_matrix.csv")
df_priority = pd.read_csv("data/priority.csv")

df_full = df_full[df_full['TA_score'] > 40]

df_full = df_full.merge(df_priority, on='subcatg', how='left', suffixes=('', '_y'))
df_full['TA_score'] = df_full['TA_score'].astype(float)
df_full['priority'] = df_full['priority'].astype(bool)

treemap_colors = {
    "treemap_good": "#059669",
    "treemap_middle": "#c5cfc4",
    "treemap_bad": "#ef4444",
}

def treemap(selected_value, df):
    size_col_name = 'TA_score'
    
    data_filtered = df.where(
        (df['TA_score'] >= selected_value[0]) & (df['TA_score'] <= selected_value[1])
    ).dropna()

    fig = px.treemap(
        data_filtered, path=['catg', 'subcatg', 'entity'], 
        values='count',
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

# Checkbox para mostrar solo subcategorías priorizadas
show_priority_only = st.checkbox("Mostrar solo subcategorías priorizadas", value=False)

# Filtrar datos según la selección del checkbox
if show_priority_only:
    # Asumiendo que las subcategorías priorizadas tienen un campo 'is_priority' o similar
    # Si no existe, puedes filtrar por otro criterio como valores no nulos en 'priority'
    df_filtered = df_full[(df_full['priority'].notna()) & (df_full['priority'] == True)]
else:
    df_filtered = df_full

print(df_filtered.shape)

# Forzar refresco cuando cambie el checkbox
if df_filtered.empty:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
    st.stop()

selected_value = st.slider(
    "Select Topical Authority Range",
    min_value=int(df_filtered['TA_score'].min()),
    max_value=int(df_filtered['TA_score'].max()),
    value=(int(df_filtered['TA_score'].min()), int(df_filtered['TA_score'].max())),
    key=f"slider_{show_priority_only}"
)

fig = treemap(selected_value, df_filtered)

st.plotly_chart(fig, use_container_width=True)