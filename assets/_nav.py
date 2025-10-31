from dash import html
import dash_bootstrap_components as dbc
import dash

_nav = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.I(className="fa-solid fa-chart-simple fa-2x")],
                className='logo'
            )
        ], width="auto"),

        dbc.Col([
            html.H1("PXS", className='app-brand')
        ], width="auto"),

        dbc.Col([
            dbc.Nav(
                [
                    dbc.NavLink(page["name"], active='exact', href=page["path"])
                    for page in dash.page_registry.values()
                ],
                vertical=False,
                pills=True,
                class_name="my-nav ms-auto"  # <-- schiebt nach rechts
            )
        ], className="d-flex justify-content-end", width=True)  # <-- rechts im Grid
    ], className="nav-bar")
], fluid=True)