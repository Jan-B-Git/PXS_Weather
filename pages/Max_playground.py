import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__)

# Read and prepare the data
df = pd.read_csv('data/Arber.csv', sep=',\s*', engine='python')  # handle spaces after comma
df.columns = df.columns.str.strip()  # remove whitespace from column names
df['DATE'] = pd.to_datetime(df['DATE'].str.strip(), format='%d.%m.%Y')
df = df.replace(-999, pd.NA)

df1 = pd.read_csv('data/Straubing.csv', sep=',\s*', engine='python')  # handle spaces after comma
df1.columns = df.columns.str.strip()  # remove whitespace from column names
df1['DATE'] = pd.to_datetime(df1['DATE'].str.strip(), format='%d.%m.%Y')
df1 = df.replace(-999, pd.NA)

df2 = pd.read_csv('data/Schorndorf.csv', sep=',\s*', engine='python')  # handle spaces after comma
df2.columns = df.columns.str.strip()  # remove whitespace from column names
df2['DATE'] = pd.to_datetime(df2['DATE'].str.strip(), format='%d.%m.%Y')
df2 = df.replace(-999, pd.NA)

# Create the figure
fig = px.line(  
    df, 
    x='DATE', 
    y='LUFTTEMPERATUR',
    title='Temperaturverlauf Arber',
    labels={'DATE': 'Datum', 'LUFTTEMPERATUR': 'Temperatur (°C)'}
)

fig1 = px.line(  
    df1, 
    x='DATE', 
    y='LUFTTEMPERATUR',
    title='Temperaturverlauf Straubing',
    labels={'DATE': 'Datum', 'LUFTTEMPERATUR': 'Temperatur (°C)'}
)

fig2 = px.line(  
    df2, 
    x='DATE', 
    y='LUFTTEMPERATUR',
    title='Temperaturverlauf Schorndorf',
    labels={'DATE': 'Datum', 'LUFTTEMPERATUR': 'Temperatur (°C)'}
)

layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([
            html.H3(['Trends Temperatur und Niederschlag']),
            html.P([html.B(['Temperatur'])], className='par')
        ], className='row-titles')
    ]),
    # Plot output
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="temperature-plot",
                figure=fig
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="temperature-plot",
                figure=fig1
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="temperature-plot",
                figure=fig2
            )
        ])
    ])
], fluid=True)