import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

import plotly.graph_objects as go

dash.register_page(__name__)



#Dataframe vorbereiten
df_A = pd.read_csv('data/Arber.csv', sep=',\s*', engine='python')  # handle spaces after comma
df_St = pd.read_csv('data/Straubing.csv', sep=',\s*', engine='python')  # handle spaces after comma
df_Sc = pd.read_csv('data/Schorndorf.csv', sep=',\s*', engine='python')  # handle spaces after comma

df_A['DATE'] = pd.to_datetime(df_A['DATE'], errors='coerce')
df_St['DATE'] = pd.to_datetime(df_St['DATE'], errors='coerce')
df_Sc['DATE'] = pd.to_datetime(df_Sc['DATE'], errors='coerce')

#Dataframe über 18 Jahre vorbereiten
df_A = df_A[(df_A['DATE'].dt.year >= 1997) & (df_A['DATE'].dt.year <= 2015)]
df_St = df_St[(df_St['DATE'].dt.year >= 1997) & (df_St['DATE'].dt.year <= 2015)]
df_Sc = df_Sc[(df_Sc['DATE'].dt.year >= 1997) & (df_Sc['DATE'].dt.year <= 2015)]

#Lufttemperatur Heatmap über 18 Jahre
df_temp = df_A[['DATE', 'LUFTTEMPERATUR']] \
    .merge(df_St[['DATE', 'LUFTTEMPERATUR']], on='DATE', how='inner', suffixes=('_arber', '_straubing')) \
    .merge(df_Sc[['DATE', 'LUFTTEMPERATUR']], on='DATE', how='inner')

df_temp.rename(columns={'LUFTTEMPERATUR':'LUFTTEMPERATUR_schorndorf'}, inplace=True)

corr_matrix = df_temp[['LUFTTEMPERATUR_arber',
                       'LUFTTEMPERATUR_straubing',
                       'LUFTTEMPERATUR_schorndorf']].corr()


# corr_matrix = df_temp[['LUFTTEMPERATUR_arber',
#                        'LUFTTEMPERATUR_straubing',
#                        'LUFTTEMPERATUR_schorndorf']].corr()


# fig_corr = go.Figure(
#     data=go.Heatmap(
#         z=corr_matrix.values,
#         x=corr_matrix.columns,
#         y=corr_matrix.columns,
#         colorscale="RdBu",
#         zmin=-1,
#         zmax=1
#     )
# )
# fig_corr.update_layout(title="Korrelationsmatrix Temperaturen")

fig_Lufttemperatur_18jahre = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale='RdBu_r',
    zmin=-1,
    zmax=1,
    aspect="auto"
)


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3(['Korrelationsanalyse']),
            html.P([html.B(['Lufttemperatur: 1997 - 2015'])], className='par')
        ], className='row-titles')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="Niederschlags-plot-arber-2015",
                figure=fig_Lufttemperatur_18jahre
            )
        ])
    ])
], fluid=True)