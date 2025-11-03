# Dash ist ein Framework, das drei Technologien vereint:
# - Flask (Backend / Webserver)
# - React (Frontend / Benutzeroberfläche)
# - Plotly (interaktive Diagramme)
#
# Dash übernimmt damit das gesamte Frontend – man muss kein eigenes HTML, CSS oder JavaScript schreiben.
# Alles wird in Python definiert, und Dash erzeugt daraus automatisch die Web-Oberfläche.

import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import pandas as pd

import base64
import datetime
import io

import pandas as pd


# ----- Seitendefinition ------------------------------------------------------------------
# Hier werden die Seiten regestiert damit app.py die Seite findet .
dash.register_page(__name__, path="/")

# == LAYOUT ============================================================================
# Das Layout beschreibt, WIE die App aussieht.
# Es funktioniert wie ein Bauplan für alle HTML-Elemente der App.
# Dash-Elemente (dcc.*, html.*, dbc.*) erzeugen tatsächliches HTML/React im Browser ohen das man das HTML selbst programmieren muss

layout = dbc.Container([

    dbc.Row([
        dbc.Col([

            # Upload-Feld für Dateien (CSV)
            dcc.Upload(
                id="upload-data",
                children=html.Div([
                    "Drag and Drop oder Datei auswählen"
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
                multiple=True,  # erlaubt mehrere Dateien
            ),
        ], className="row-titles", width=12),

        # Speicherbereich in Dash – speichert Daten unsichtbar im Browser
        dcc.Store(id="stored-data"),
        # Plot-Ausgabe (Plotly Graph)
        dbc.Col([
            dcc.Graph(
                id="line-plot",
                 style={"height": "600px"}
                ),
        ],width=12),
        dbc.Row([
            # Dropdown zur Auswahl der Spalten für den Plot (wird dynamisch gefüllt)
            dbc.Col([
                dcc.Dropdown(id="columns", options=["test","test2"], multi=True),
            ],width=9),
            dbc.Col([
                dcc.Checklist(
                    id="missing-data",
                    options=["remove missing data"],
                    value=["remove missing data"],
                    ),
            ],width=3),
            ])
        ]),
        # Hier wird die Tabelle nach Upload angezeigt
        html.Div(id="output-data-upload"),
], fluid=True, className="full-layout")


# == FUNKTION: Datei einlesen ============================================================
def parse_contents(contents, filename, date):
    # contents enthält den Dateicontent als Base64-String, den dekodieren wir
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    try:
        # falls CSV → per Pandas einlesen
        if "csv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        print(e)
        return html.Div(["Fehler beim Lesen der Datei."])

    # Anzeige der Tabelle in Dash
    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],

            fixed_rows={"headers": True},
            style_table={
                "height": "1000px",
                "overflowY": "auto",
                "overflowX": "auto"
            },
            style_cell={"textAlign": "left"},
        )
    ])


# == CALLBACK 1: Datei einlesen + Tabelle anzeigen + Dropdown füllen ======================
# CALLBACKS verknüpfen Benutzeraktionen (Input) mit Reaktionen der App (Output).
# Dash überwacht Inputs und ruft automatisch die Callback-Funktion auf,
# wenn sich etwas ändert (z.B. Datei hochgeladen, Dropdown geändert).

@callback(
    Output("output-data-upload", "children"),  # zeigt Tabelle an
    Output("stored-data", "data"),             # speichert Daten im Browser
    Output("columns", "options"),              # füllt Dropdown mit Spaltennamen
    Input("upload-data", "contents"),          # Callback startet wenn Datei hochgeladen wird
    State("upload-data", "filename"),          # State befehle sind wie Input nur das sie den callback nciht starten sondern nur wenn er schon aktiv ist die daten bereit stellt
    State("upload-data", "last_modified")
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        # erstellt für jede Datei eine Tabelle
        parsed = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)
        ]

        # Daten der ersten CSV speichern
        df = pd.read_csv(
            io.StringIO(base64.b64decode(list_of_contents[0].split(",")[1]).decode("utf-8"))
        )

        header = list(df.columns)

        return parsed, df.to_dict("records"), header

    return None, None, []


# == CALLBACK 2: Plot zeichnen ============================================================

@callback(
    Output("line-plot", "figure"),
    Input("stored-data", "data"),     # Daten aus Store
    Input("columns", "value"),        # ausgewählte Spalten aus Dropdown
    Input("missing-data","value"),
)   
def update_plot(data, headers,missing_data):
    if data is None:
        return {}

    df = pd.DataFrame(data)
    x = df.columns[0]

    if not headers:
        return None

    # Plotly Figure: definiert Daten + Layout
    fig = {
        "data": [],
        "layout": {
            "legend": {
                "orientation": "h", 
                "yanchor": "bottom",
                "y": 1.05,
                "xanchor": "center",
                "x": 0.5
            },
            "margin": {"l": 40, "r": 40, "t": 80, "b": 120}
        }
    }
    if missing_data:
        df = df.replace(-999, pd.NA)

    for h in headers:
        fig["data"].append({
            "type": "line",
            "x": df[x],
            "y": df[h],
            "name": h,
            "layout": {
                "title": f"Liniendiagramm: {', '.join(headers)} vs. {x}",
                "legend": {
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": 1.05,
                    "xanchor": "center",
                    "x": 0.5
                },
                "margin": {"l": 40, "r": 40, "t": 80, "b": 80}
}
        })

    return fig