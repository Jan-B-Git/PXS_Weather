import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import pandas as pd

import base64
import datetime
import io

import pandas as pd


dash.register_page(__name__)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                    id="upload-data",
                    children=html.Div([
                        "Drag and Drop or ",
                    ]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    multiple=True
    )], className="row-titles"),
    dcc.Store(id="stored-data"),
    dcc.Graph(id="line-plot",),
    dcc.Dropdown(id="columns",options=["test","test2"], multi=True),
    html.Div(id="output-data-upload")
    ]),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        print(e)
        return html.Div([
            "There was an error processing this file."
        ])
    return html.Div([
        html.H5(filename),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            fixed_rows={'headers': True}, 

            style_table={
                "height": '1000px',
                "overflowY": "auto", 
                "overflowX": "auto"  
            },
            style_cell={"textAlign": "left"},
        )
    ])

###---- Tabelle 
@callback(
    Output("output-data-upload", "children"),
    Output("stored-data", "data"),
    Output("columns","options"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified")
)

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        parsed = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)
        ]

        df = pd.read_csv(
            io.StringIO(base64.b64decode(list_of_contents[0].split(",")[1]).decode("utf-8"))
        )
        header=list(df.columns)

        return parsed, df.to_dict("records"),header

    return None, None

###---- Plot
@callback(
    Output("line-plot", "figure"),
    Input("stored-data", "data"),
    Input("columns", "value"),
)
def update_plot(data,headers):
    if data is None:
        return {}
    df = pd.DataFrame(data)

    
    x = df.columns[0]


    fig = {
        "data": [],
        "layout": {
            "title": f"Line Plot: {', '.join(headers)} vs. {x}"
        }
    }

    for h in headers:
        fig["data"].append({
            "type": "line",
            "x": df[x],
            "y": df[h],
            "name": h  
        })

    return fig
