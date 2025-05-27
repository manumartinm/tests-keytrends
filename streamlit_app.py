import streamlit as st
import pandas as pd
import plotly.express as px

df_full = pd.read_csv("data/grouped_matrix.csv")
df_full['TA_score'] = df_full['TA_score'].astype(float)

df_full = df_full[df_full['TA_score'] > 40]
treemap_colors = {
    "treemap_good": "#059669",
    "treemap_middle": "#c5cfc4",
    "treemap_bad": "#ef4444",
}

def treemap(selected_value, df):
    size_col_name = 'count'
    
    data_filtered = df.where(
        (df['TA_score'] >= selected_value[0]) & (df['TA_score'] <= selected_value[1])
    ).dropna()

    fig = px.treemap(
        data_filtered, path=['catg', 'subcatg', 'entity'], values='TA_score',
        color=size_col_name, 
        color_continuous_scale=[
            treemap_colors['treemap_good'], 
            treemap_colors['treemap_middle'], 
            treemap_colors['treemap_bad']
        ],
    )
    fig.update_traces(marker=dict(cornerradius=5), root_color="lightgrey")
    
    return fig

st.title("Entities Trends Treemap")
selected_value = st.slider(
    "Select Topical Authority Range",
    min_value=int(df_full['TA_score'].min()),
    max_value=int(df_full['TA_score'].max()),
    value=(int(df_full['TA_score'].min()), int(df_full['TA_score'].max())),
)

fig = treemap(selected_value, df_full)

st.plotly_chart(fig, use_container_width=True)
