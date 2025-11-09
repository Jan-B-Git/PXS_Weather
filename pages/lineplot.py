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
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import os
from pathlib import Path

# ----- Seitendefinition ------------------------------------------------------------------
dash.register_page(__name__, path="/")

# Funktion um CSV-Dateien aus dem data-Ordner zu laden
def get_csv_files_from_data_folder():
    """Liest alle CSV-Dateien aus dem 'data' Ordner"""
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
                            dcc.Dropdown(id="plots", options=["line-plot","heatmap"], placeholder="Select Plot type...", style={"margin": "15px 0"}),
                        ], width=6),
                    ]),
                ], width=7),
                dbc.Col([
                    html.H4("Settings", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Checklist(
                                id="missing-data",
                                options=["Remove Missing Data"],
                                value=[],
                                style={"margin": "10px 0"}
                            ),
                            dcc.Checklist(
                                id="common-timerange",
                                options=["Common Timerange"],
                                value=[],
                                style={"margin": "10px 0"}
                            ),
                            dcc.Checklist(
                                id="yearly-mean",
                                options=["Yearly Mean"],
                                value=[],
                                style={"margin": "10px 0"}
                            ),
                            dcc.Checklist(
                                id="snowdays",
                                options=["Snow days"],
                                value=[],
                                style={"margin": "10px 0"}
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
            
            # Speicherbereich in Dash – speichert Daten unsichtbar im Browser
            dcc.Store(id="stored-data"),
            dcc.Store(id="csv-files-data"),
            
            dbc.Row([
                # Plot-Ausgabe
                dbc.Col([
                    dcc.Graph(
                        id="line-plot",
                        style={"height": "600px", "margin":"15px"},
                    ),
                ], width=12),
            ]),
        ]),
        
        # Tab 2: Tabellen-Ansicht
        dcc.Tab(label="Data table", value="tab-table", children=[
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
        return None, [], html.Div("No Data choiced")
    
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
                # Versuche verschiedene Datumsformate
                if df[x_column].dtype == 'object':
                    # Format DD.MM.YYYY (z.B. 10.06.2011)
                    if '.' in str(df[x_column].iloc[0]):
                        df[x_column] = pd.to_datetime(df[x_column], format='%d.%m.%Y', errors='coerce')
                    # Format YYYYMMDD (z.B. 20110610)
                    elif len(str(df[x_column].iloc[0])) == 8:
                        df[x_column] = pd.to_datetime(df[x_column], format='%Y%m%d', errors='coerce')
                    else:
                        df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
                else:
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
    Input("moving-average-window", "value"),
    Input("common-timerange","value"),
    Input("plots","value"),
    Input("yearly-mean","value"),
    Input("snowdays","value")
)   
def update_plot(all_data, selected_columns, missing_data, window_years,common_timerange,plot_type,yearly_mean,snowdays):
    if not all_data or not selected_columns and not snowdays:
        return {
            "data": [],
            "layout": {
                "title": "Pls choice CSV data and a column",
                "xaxis": {"title": "X"},
                "yaxis": {"title": "Y"}
            }
        }

    common_start=None
    common_end=None
    if common_timerange:
        for filename, data in all_data.items():
            df = pd.DataFrame(data)
            x_col = df.columns[0]
            df[x_col] = pd.to_datetime(df[x_col], errors='coerce')
            df = df.sort_values(by=x_col).reset_index(drop=True)
            if missing_data:
                df = df.replace(-999, float('nan'))

            if common_end is None and common_end is None:
                common_start = df[x_col].min() 
                common_end = df[x_col].max() 
            common_start = df[x_col].min()  if common_start < df[x_col].min()  else common_start
            common_end = df[x_col].max()  if common_end > df[x_col].max()  else common_end


    window_days = int(window_years * 365) if window_years > 0 else 0
     

    fig = go.Figure()

    heatmap_z = []
    heatmap_ylabels = []

    for filename, data in all_data.items():
        df = pd.DataFrame(data)
        x_column = df.columns[0]
        df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
        df = df.sort_values(by=x_column).reset_index(drop=True)

        if missing_data:
            df = df.replace(-999, float('nan'))

        if common_timerange and common_start is not None and common_end is not None:
            df = df[(df[x_column] >= common_start) & (df[x_column] <= common_end)]
    

        if  snowdays:
            df["year"] = df[x_column].dt.year
            snow_days=df[" SCHNEEHOEHE"].gt(0).groupby(df["year"]).sum()
            return  fig.add_trace(go.Scatter(
                        x=snow_days.index,
                        y=snow_days,
                        mode="lines"
                    ))



        # Spalten durchgehen
        for col in selected_columns:
            
            if col in df.columns and col != x_column:
                df[col] = pd.to_numeric(df[col], errors='coerce')

                df["year"] = df[x_column].dt.year
                annual_mean = df.groupby("year")[col].mean()


                # x = Jahre, y = Mittelwerte
                x_mean = annual_mean.index
                y_mean = annual_mean.values

                y = df[col].rolling(window=window_days, center=True, min_periods=1).mean() \
                    if window_days > 0 else df[col]

                if plot_type == "line-plot":
                    if yearly_mean:
                        x=x_mean
                        y=y_mean
                    else:
                        x=df[x_column]

                    fig.add_trace(go.Scatter(
                        x=x,
                        y=y,
                        name=f"{filename} - {col}",
                        mode="lines"
                    ))

                if plot_type == "heatmap":
                    heatmap_z.append(y.tolist())
                    heatmap_ylabels.append(f"{filename} - {col}")


    if plot_type == "heatmap":
        fig.add_trace(go.Heatmap(
            z=heatmap_z,
            x=df[x_column],
            y=heatmap_ylabels,
            colorscale="Viridis"
        ))

    fig.update_layout(
        xaxis={"type": "date", "title": "Datum"},
        yaxis={"title": "Wert"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.05, "xanchor": "center", "x": 0.5},
        margin={"l": 40, "r": 40, "t": 80, "b": 120}
    )

    return fig