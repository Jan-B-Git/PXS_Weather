import dash
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

dash.register_page(__name__)

#Dataframe vorbereiten
df_A = pd.read_csv('data/Arber.csv', sep=r',\s*', engine='python')
df_St = pd.read_csv('data/Straubing.csv', sep=r',\s*', engine='python')
df_Sc = pd.read_csv('data/Schorndorf.csv', sep=r',\s*', engine='python')

df_A['DATE'] = pd.to_datetime(df_A['DATE'], errors='coerce')
df_St['DATE'] = pd.to_datetime(df_St['DATE'], errors='coerce')
df_Sc['DATE'] = pd.to_datetime(df_Sc['DATE'], errors='coerce')

#Dataframe über 18 Jahre vorbereiten
df_A = df_A[(df_A['DATE'].dt.year >= 1997) & (df_A['DATE'].dt.year <= 2015)]
df_St = df_St[(df_St['DATE'].dt.year >= 1997) & (df_St['DATE'].dt.year <= 2015)]
df_Sc = df_Sc[(df_Sc['DATE'].dt.year >= 1997) & (df_Sc['DATE'].dt.year <= 2015)]

# Dictionary mit allen verfügbaren Spalten für Korrelationen
available_columns = {
    'LUFTTEMPERATUR': 'Lufttemperatur',
    'NIEDERSCHLAGSHOEHE': 'Niederschlagshöhe',
    'LUFTTEMP_AM_ERDB_MAXIMUM': 'Lufttemperatur Maximum',
    'LUFTTEMP_AM_ERDB_MINIMUM': 'Lufttemperatur Minimum',
    'WINDSPITZE_MAXIMUM': 'Windspitze Maximum',
    'SCHNEEHOEHE': 'Schneehöhe',
    'DAMPFDRUCK': 'Dampfdruck',
    'BEDECKUNGSGRAD': 'Bedeckungsgrad',
    'WINDGESCHWINDIGKEIT': 'Windgeschwindigkeit',
    'SONNENSCHEINDAUER': 'Sonnenscheindauer'
}

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3(['Korrelationsanalyse']),
            html.P([html.B(['1997 - 2015'])], className='par')
        ], className='row-titles')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='correlation-column-dropdown',
                options=[{'label': v, 'value': k} for k, v in available_columns.items()],
                value='LUFTTEMPERATUR',
                clearable=False,
                style={'width': '400px'}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='correlation-heatmap')
        ])
    ])
], fluid=True)

@callback(
    Output('correlation-heatmap', 'figure'),
    Input('correlation-column-dropdown', 'value')
)
def update_heatmap(selected_column):
    # Merge dataframes
    df_merged = df_A[['DATE', selected_column]] \
        .merge(df_St[['DATE', selected_column]], on='DATE', how='inner', suffixes=('_arber', '_straubing')) \
        .merge(df_Sc[['DATE', selected_column]], on='DATE', how='inner')
    
    df_merged.rename(columns={selected_column: f'{selected_column}_schorndorf'}, inplace=True)
    
    # Calculate correlation matrix
    corr_matrix = df_merged[[f'{selected_column}_arber',
                              f'{selected_column}_straubing',
                              f'{selected_column}_schorndorf']].corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect="auto",
        title=f'Korrelationsmatrix {available_columns[selected_column]}: 1997 - 2015'
    )
    
    return fig