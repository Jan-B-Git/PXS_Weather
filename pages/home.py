import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([
            html.H3(['Welcome!']),
            html.P([html.B(['App Overview'])], className='par')
        ], width=12, className='row-titles')
    ]),
])