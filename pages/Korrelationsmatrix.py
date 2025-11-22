import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3(['Trends Temperatur und Niederschlag']),
            html.P([html.B(['Temperatur'])], className='par')
        ], className='row-titles')
    ])
], fluid=True)