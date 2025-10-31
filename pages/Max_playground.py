import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([
            html.H3(['Ganz viel spaß Max !']),
            html.P([html.B(['Top dich hier aus'])], className='par')
        ], className='row-titles')
    ]),
],fluid=True)