from dash import Dash, dcc
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
	   suppress_callback_exceptions=True, prevent_initial_callbacks=True)
server = app.server

############################################################################################
# Import shared components

from assets._nav import _nav

############################################################################################
# App Layout
app.layout = dbc.Container([
	
	dbc.Row([
        dbc.Col([_nav], width = 12),
        dbc.Col([
            dbc.Row([dash.page_container])
	    ], width = 12),
    ]),
     dcc.Store(id='browser-memo', data=dict(), storage_type='session')
], fluid=True)

############################################################################################
# Run App
if __name__ == '__main__':
	app.run(debug=True)