# Dash ist ein Framework, das drei Technologien vereint:
# - Flask (Backend / Webserver)
# - React (Frontend / Benutzeroberfläche)
# - Plotly (interaktive Diagramme)
#
# Dash übernimmt damit das gesamte Frontend – man muss kein eigenes HTML, CSS oder JavaScript schreiben.
# Alles wird in Python definiert, und Dash erzeugt daraus automatisch die Web-Oberfläche.

import dash
from dash import html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import os
from pathlib import Path

# ----- Seitendefinition ------------------------------------------------------------------
dash.register_page(__name__, path="/")

# Funktion um CSV-Dateien aus dem data-Ordner zu laden
def get_csv_files_from_data_folder():
    data_folder = Path("data")
    if not data_folder.exists():
        return []
    csv_files = [f.stem for f in data_folder.glob("*.csv")]
    return csv_files

# == LAYOUT ============================================================================
layout = dbc.Container([
    # Tabs für Plot und Tabelle
    dcc.Tabs(id="tabs", value="tab-plot", children=[
        # Tab 1: Plot-Ansicht
        dcc.Tab(label="Plot", value="tab-plot", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Choice Data", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Checklist(
                                id="csv-file-selector",
                                options=[],
                                value=[],
                                labelStyle={"display": "inline-block", "margin-right": "15px", "margin-top":"15px"}
                            ),
                        ], width=6),
                        dbc.Col([
                            dcc.Dropdown(id="columns", options=[], multi=True, placeholder="Select Column ...", style={"margin": "15px 0"}),
                        ], width=6),
                    ]),
                ], width=7),
                dbc.Col([
                    html.H4("Settings", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Checklist(
                                id="missing-data",
                                options=["remove missing data"],
                                value=["remove missing data"],
                                style={"margin": "15px 0"}
                            ),
                        ], width=6),
                        dbc.Col([ 
                            html.Label("Moving Average (Years)"),
                            dcc.Slider(
                                min=0,
                                max=5,
                                step=0.5,
                                value=0,
                                id="moving-average-window",
                                marks={i: f"{i}" for i in range(6)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                        ], width=6)
                    ])
                ], width=5),
            ]),
            
            dcc.Store(id="stored-data"),
            dcc.Store(id="csv-files-data"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id="line-plot",
                        style={"height": "600px", "margin":"15px"},
                    ),
                ], width=12),
            ]),
        ]),
        
        # Tab 2: Tabellen-Ansicht
        dcc.Tab(label="Daten Tabelle", value="tab-table", children=[
            html.Div(id="output-data-upload", className="mt-3"),
        ]),
    ]),
], fluid=True, className="full-layout")


# == CALLBACK: CSV-Dateien aus Ordner laden ============================================
@callback(
    Output("csv-file-selector", "options"),
    Input("tabs", "value")  # Lädt beim Start/Tab-Wechsel
)
def load_csv_options(_):
    """Füllt die Checkbox-Liste mit verfügbaren CSV-Dateien"""
    csv_files = get_csv_files_from_data_folder()
    return [{"label": f, "value": f} for f in csv_files]


# == CALLBACK: Ausgewählte CSVs laden ===================================================
@callback(
    Output("csv-files-data", "data"),
    Output("columns", "options"),
    Output("output-data-upload", "children"),
    Input("csv-file-selector", "value"),
)
def load_selected_csvs(selected_files):
    """Lädt alle ausgewählten CSV-Dateien"""
    if not selected_files:
        return None, [], html.Div("Keine Dateien ausgewählt")
    
    data_folder = Path("data")
    all_data = {}
    all_columns = set()
    tables = []
    
    for filename in selected_files:
        filepath = data_folder / f"{filename}.csv"
        try:
            df = pd.read_csv(filepath)
            
            # Erste Spalte als Datetime behandeln und sortieren
            x_column = df.columns[0]
            try:
                df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
                df = df.sort_values(by=x_column).reset_index(drop=True)
                # Als String speichern für JSON-Kompatibilität
                df[x_column] = df[x_column].dt.strftime('%Y-%m-%d')
            except:
                pass
            
            all_data[filename] = df.to_dict("records")
            all_columns.update(df.columns.tolist())
            
            # Tabelle für Tab 2 erstellen
            tables.append(html.Div([
                html.H5(filename, className="mt-3"),
                dash_table.DataTable(
                    data=df.to_dict("records"),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    fixed_rows={"headers": True},
                    style_table={
                        "height": "400px",
                        "overflowY": "auto",
                        "overflowX": "auto"
                    },
                    style_cell={"textAlign": "left"},
                )
            ]))
        except Exception as e:
            tables.append(html.Div([
                html.H5(filename, style={"color": "red"}),
                html.P(f"Fehler beim Laden: {str(e)}")
            ]))
    
    # Spaltenoptionen für Dropdown (ohne erste Spalte = X-Achse)
    column_options = sorted(list(all_columns))
    
    return all_data, column_options, html.Div(tables)

    
# == CALLBACK: Plot zeichnen ============================================================
@callback(
    Output("line-plot", "figure"),
    Input("csv-files-data", "data"),
    Input("columns", "value"),
    Input("missing-data", "value"),
    Input("moving-average-window", "value")
)   
def update_plot(all_data, selected_columns, missing_data, window_years):
    """Erstellt Plot mit Daten aus mehreren CSVs"""
    if not all_data or not selected_columns:
        return {
            "data": [],
            "layout": {
                "title": "Bitte CSV-Dateien und Spalten auswählen",
                "xaxis": {"title": "X"},
                "yaxis": {"title": "Y"}
            }
        }
    
    # Fenster in Tage umrechnen
    window_days = int(window_years * 365) if window_years > 0 else 0
    

    
    fig = {
        "data": [],
        "layout": {
            "xaxis": {
                "type": "date",
                "title": "Datum"
            },
            "yaxis": {
                "title": "Wert"
            },
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
    
    # Durch alle CSV-Dateien iterieren
    for filename, data in all_data.items():
        df = pd.DataFrame(data)
        x_column = df.columns[0]
        
        # Datumsspalte zurück zu Datetime konvertieren und sortieren
        df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
        df = df.sort_values(by=x_column).reset_index(drop=True)
        
        # Missing data behandeln - erst zu NaN konvertieren
        if missing_data:
            df = df.replace(-999, float('nan'))
        
        # Für jede ausgewählte Spalte eine Linie hinzufügen
        for col in selected_columns:
            if col in df.columns and col != x_column:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                if window_days > 0:
                    y = df[col].rolling(window=window_days, center=True,min_periods=1).mean()
                else:
                    y = df[col]
                
                fig["data"].append({
                    "type": "scatter",
                    "x": df[x_column],
                    "y": y,
                    "name": f"{filename} - {col}",
                    "mode": "lines"
                })
    
    return fig