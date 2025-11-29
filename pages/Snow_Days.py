import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# ----- Seitendefinition ------------------------------------------------------------------
dash.register_page(__name__, path="/snow")

# Funktion um CSV-Dateien aus dem data-Ordner zu laden
def get_csv_files_from_data_folder():
    """Liest alle CSV-Dateien aus dem 'data' Ordner"""
    data_folder = Path("data")
    if not data_folder.exists():
        return []
    csv_files = [f.stem for f in data_folder.glob("*.csv")]
    return csv_files

def load_and_clean_snow_data(filename):
    """
    Lädt CSV-Datei und bereinigt Schneehöhen-Daten
    - Lädt nur Datum und Schneehöhe
    - Ersetzt -999 mit NaN
    - Konvertiert Datum
    - Sortiert nach Datum
    """
    data_folder = Path("data")
    filepath = data_folder / f"{filename}.csv"
    
    try:
        df = pd.read_csv(filepath, usecols=["DATE", " SCHNEEHOEHE"])
        
        # Erste Spalte als Datetime behandeln
        x_column = df.columns[0]
        
        # Datum konvertieren
        if df[x_column].dtype == 'object':
            if '.' in str(df[x_column].iloc[0]):
                df[x_column] = pd.to_datetime(df[x_column], format='%d.%m.%Y', errors='coerce')
            elif len(str(df[x_column].iloc[0])) == 8:
                df[x_column] = pd.to_datetime(df[x_column], format='%Y%m%d', errors='coerce')
            else:
                df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
        else:
            df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
        
        # Nach Datum sortieren
        df = df.sort_values(by=x_column).reset_index(drop=True)
        
        # -999 durch NaN ersetzen
        df[" SCHNEEHOEHE"] = df[" SCHNEEHOEHE"].replace(-999, float('nan'))
        
        # Jahr und Monat als separate Spalten hinzufügen
        df['year'] = df[x_column].dt.year
        df['month'] = df[x_column].dt.month

        return df, x_column
        
    except Exception as e:
        print(f"Fehler beim Laden von {filename}: {str(e)}")
        return None, None


# == LAYOUT ============================================================================
layout = dbc.Container([    
    dbc.Row([
        dbc.Col([
            html.H4("Datei-Auswahl"),
            dcc.Dropdown(
                id="snow-csv-selector",
                options=[],
                value=None,
                placeholder="CSV-Datei auswählen..."
            ),
        ], width=6),
    ], className="mb-4"),
    
    # Speicher für geladene Daten
    dcc.Store(id="snow-data-store"),
    
    # Tabs für verschiedene Ansichten
    dcc.Tabs(id="snow-tabs", value="tab-timeseries", children=[
        # Tab 1: Zeitreihen-Plot
        dcc.Tab(label="Zeitreihe", value="tab-timeseries", children=[
            dcc.Graph(
                id="snow-timeseries-plot",
                style={"height": "600px", "margin": "15px"}
            ),
        ]),
        
        # Tab 2: Jährliche Statistiken
        dcc.Tab(label="Jährliche Auswertung", value="tab-yearly", children=[
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id="snow-days-per-year",
                        style={"height": "500px", "margin": "15px"}
                    ),
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id="snow-max-per-year",
                        style={"height": "500px", "margin": "15px"}
                    ),
                ], width=6),
            ]),
        ]),
    ]),
    
], fluid=True)


# == CALLBACK: CSV-Optionen laden ======================================================
@callback(
    Output("snow-csv-selector", "options"),
    Input("snow-tabs", "value")
)
def load_snow_csv_options(_):
    """Lädt verfügbare CSV-Dateien"""
    csv_files = get_csv_files_from_data_folder()
    return [{"label": f, "value": f} for f in csv_files]


# == CALLBACK: Daten laden =============================================================
@callback(
    Output("snow-data-store", "data"),
    Input("snow-csv-selector", "value"),
)
def load_snow_data(selected_file):
    """Lädt ausgewählte CSV und bereitet Daten auf"""
    if not selected_file:
        return None
    
    df, x_column = load_and_clean_snow_data(selected_file)
    
    if df is None:
        return None
    
    # Daten als JSON speichern
    data_json = {
        "df": df.to_dict("records"),
        "x_column": x_column,
        "filename": selected_file
    }
    
    return data_json


# == CALLBACK: Zeitreihen-Plot =========================================================
@callback(
    Output("snow-timeseries-plot", "figure"),
    Input("snow-data-store", "data"),
)
def update_timeseries_plot(data_json):
    """Erstellt Zeitreihen-Plot der Schneehöhe"""
    if not data_json:
        return {
            "data": [],
            "layout": {
                "title": "Bitte Datei auswählen",
                "xaxis": {"title": "Datum"},
                "yaxis": {"title": "Schneehöhe (cm)"}
            }
        }
    
    df = pd.DataFrame(data_json["df"])
    x_column = data_json["x_column"]
    df[x_column] = pd.to_datetime(df[x_column])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_column],
        y=df[" SCHNEEHOEHE"],
        mode="lines",
        name="Schneehöhe",
        line={"color": "steelblue"}
    ))
    
    fig.update_layout(
        title=f"Schneehöhe - {data_json['filename']}",
        xaxis={"title": "Datum", "type": "date"},
        yaxis={"title": "Schneehöhe (cm)"},
        hovermode="x unified",
        template="plotly_white"
    )
    
    return fig


# == CALLBACK: Jährliche Schneetage ====================================================
@callback(
    Output("snow-days-per-year", "figure"),
    Input("snow-data-store", "data"),
)
def update_snow_days_per_year(data_json):
    """Zeigt Anzahl Schneetage pro Jahr"""
    if not data_json:
        return {"data": [], "layout": {"title": "Keine Daten"}}
    
    df = pd.DataFrame(data_json["df"])
    
    # Schneetage zählen (Schneehöhe > 0)
    snow_days_per_year = df[df[" SCHNEEHOEHE"] > 0].groupby("year").size()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=snow_days_per_year.index,
        y=snow_days_per_year.values,
        marker={"color": "lightblue"},
        name="Schneetage"
    ))
    
    fig.update_layout(
        title="Anzahl Schneetage pro Jahr",
        xaxis={"title": "Jahr"},
        yaxis={"title": "Anzahl Tage mit Schnee"},
        template="plotly_white"
    )
    
    return fig


# == CALLBACK: Maximale Schneehöhe pro Jahr ============================================
@callback(
    Output("snow-max-per-year", "figure"),
    Input("snow-data-store", "data"),
)
def update_max_snow_per_year(data_json):
    """Zeigt maximale Schneehöhe pro Jahr"""
    if not data_json:
        return {"data": [], "layout": {"title": "Keine Daten"}}
    
    df = pd.DataFrame(data_json["df"])
    
    # Maximale Schneehöhe pro Jahr
    max_snow_per_year = df.groupby("year")[" SCHNEEHOEHE"].max()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=max_snow_per_year.index,
        y=max_snow_per_year.values,
        marker={"color": "steelblue"},
        name="Max. Schneehöhe"
    ))
    
    fig.update_layout(
        title="Maximale Schneehöhe pro Jahr",
        xaxis={"title": "Jahr"},
        yaxis={"title": "Schneehöhe (cm)"},
        template="plotly_white"
    )
    
    return fig