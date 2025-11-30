import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# ----- Page Definition ------------------------------------------------------------------
dash.register_page(__name__, path="/snow")

# Funktion um CSV-Dateien aus dem data-Ordner zu laden
def get_csv_files_from_data_folder():
    """Reads all CSV files from 'data' folder"""
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
        # Erst alle Spalten laden um zu sehen welche verfügbar sind
        df_test = pd.read_csv(filepath, nrows=1)
        
        # Erste Spalte (Datum)
        x_column = df_test.columns[0]
        
        # Versuche mit verschiedenen möglichen Spaltennamen für Schnee
        snow_column = None
        for col_name in [" SCHNEEHOEHE", "SCHNEEHOEHE", "Schneehoehe", "schneehoehe"]:
            if col_name in df_test.columns:
                snow_column = col_name
                break
        
        if snow_column is None:
            print(f"FEHLER: Keine Schneehöhen-Spalte gefunden in {df_test.columns.tolist()}")
            return None, None
        
        
        # Jetzt richtig laden - mit Spaltennamen statt Index
        df = pd.read_csv(filepath, usecols=[x_column, snow_column])
        
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
        df[snow_column] = df[snow_column].replace(-999, float('nan'))
        
        # Spalte umbenennen zu Standard-Name
        df = df.rename(columns={snow_column: "SCHNEEHOEHE"})
        
        # Jahr und Monat als separate Spalten hinzufügen
        df['year'] = df[x_column].dt.year
        df['month'] = df[x_column].dt.month
        
        
        return df, x_column
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, None


# == LAYOUT ============================================================================
layout = dbc.Container([    
    dbc.Row([
        dbc.Col([
            html.H4("SELECT DATA"),
            dcc.Dropdown(
                id="snow-csv-selector",
                options=[],
                value=[],
                multi=True,
                placeholder="Select CSV file(s)..."
            ),
        ], width=6),
        dbc.Col([
            html.H5("SETTINGS"),
            dcc.Checklist(
                id="snow-analysis-options",
                options=[
                    {"label": "Common Timerange", "value": "common_timerange"},
                ],
                value=[],
                labelStyle={"display": "block", "margin": "10px 0"}
            ),
        ], width=6),
    ], className="mb-4"),
    
    # Store for loaded data
    dcc.Store(id="snow-data-store"),
    
    # Tabs for different views
    dcc.Tabs(id="snow-tabs", value="tab-timeseries", children=[
        # Tab 1: Timeseries plot
        dcc.Tab(label="TIMESERIES", value="tab-timeseries", children=[
            dcc.Graph(
                id="snow-timeseries-plot",
                style={"height": "600px", "margin": "15px"}
            ),
        ]),
        
        # Tab 2: Yearly statistics
        dcc.Tab(label="YEARLY ANALYSIS", value="tab-yearly", children=[
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
    """Loads available CSV files"""
    csv_files = get_csv_files_from_data_folder()
    return [{"label": f, "value": f} for f in csv_files]


# == CALLBACK: Daten laden =============================================================
@callback(
    Output("snow-data-store", "data"),
    Input("snow-csv-selector", "value"),
)
def load_snow_data(selected_files):
    """Loads selected CSV(s) and prepares data"""
    if not selected_files:
        return None
    
    # Falls einzelne Datei als String übergeben wird
    if isinstance(selected_files, str):
        selected_files = [selected_files]
    
    all_data = {}
    
    for filename in selected_files:
        df, x_column = load_and_clean_snow_data(filename)
        
        if df is not None:
            all_data[filename] = {
                "df": df.to_dict("records"),
                "x_column": x_column
            }
    
    if not all_data:
        return None
    
    return all_data


# == CALLBACK: Zeitreihen-Plot =========================================================
@callback(
    Output("snow-timeseries-plot", "figure"),
    Input("snow-data-store", "data"),
    Input("snow-analysis-options", "value"),
)
def update_timeseries_plot(all_data, options):
    """Creates timeseries plot of snow depth"""
    if not all_data:
        return {
            "data": [],
            "layout": {
                "title": "Please select file(s)",
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Snow Depth (cm)"}
            }
        }
    
    # Determine common time range?
    common_start = None
    common_end = None
    
    if "common_timerange" in options:
        for filename, data in all_data.items():
            df = pd.DataFrame(data["df"])
            x_col = data["x_column"]
            df[x_col] = pd.to_datetime(df[x_col], errors='coerce')
            
            if common_start is None and common_end is None:
                common_start = df[x_col].min()
                common_end = df[x_col].max()
            else:
                # Largest minimum and smallest maximum = overlap
                common_start = max(common_start, df[x_col].min())
                common_end = min(common_end, df[x_col].max())
    
    fig = go.Figure()
    
    for filename, data in all_data.items():
        df = pd.DataFrame(data["df"])
        x_column = data["x_column"]
        df[x_column] = pd.to_datetime(df[x_column])
        
        # Filter common time range
        if common_start is not None and common_end is not None:
            df = df[(df[x_column] >= common_start) & (df[x_column] <= common_end)]
        
        # Show all files in one plot
        fig.add_trace(go.Scatter(
            x=df[x_column],
            y=df["SCHNEEHOEHE"],
            mode="lines",
            name=filename,
        ))
    
    title = "Snow Depth"
    if "common_timerange" in options and common_start and common_end:
        title += f" (Period: {common_start.strftime('%Y-%m-%d')} - {common_end.strftime('%Y-%m-%d')})"
    
    fig.update_layout(
        title=title,
        xaxis={"title": "Date", "type": "date"},
        yaxis={"title": "Snow Depth (cm)"},
        hovermode="x unified",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02}
    )
    
    return fig


# == CALLBACK: Jährliche Schneetage ====================================================
@callback(
    Output("snow-days-per-year", "figure"),
    Input("snow-data-store", "data"),
    Input("snow-analysis-options", "value"),
)
def update_snow_days_per_year(all_data, options):
    """Shows number of snow days per year"""
    if not all_data:
        return {"data": [], "layout": {"title": "No Data"}}
    
    common_start = None
    common_end = None
    
    if "common_timerange" in options:
        for filename, data in all_data.items():
            df = pd.DataFrame(data["df"])
            x_col = data["x_column"]
            df[x_col] = pd.to_datetime(df[x_col], errors='coerce')
            
            if common_start is None and common_end is None:
                common_start = df[x_col].min()
                common_end = df[x_col].max()
            else:
                common_start = max(common_start, df[x_col].min())
                common_end = min(common_end, df[x_col].max())
    
    fig = go.Figure()
    
    for filename, data in all_data.items():
        df = pd.DataFrame(data["df"])
        x_column = data["x_column"]
        df[x_column] = pd.to_datetime(df[x_column])
        
        # Filter common time range
        if common_start is not None and common_end is not None:
            df = df[(df[x_column] >= common_start) & (df[x_column] <= common_end)]
        
        # Count snow days (snow depth > 0)
        snow_days_per_year = df[df["SCHNEEHOEHE"] > 0].groupby("year").size()
        
        fig.add_trace(go.Bar(
            x=snow_days_per_year.index,
            y=snow_days_per_year.values,
            name=filename
        ))
    
    title = "Number of Snow Days per Year"
    if "common_timerange" in options and common_start and common_end:
        title += f" ({common_start.year} - {common_end.year})"
    
    fig.update_layout(
        title=title,
        xaxis={"title": "Year"},
        yaxis={"title": "Number of Days with Snow"},
        template="plotly_white",
        barmode='group'
    )
    
    return fig


# == CALLBACK: Maximale Schneehöhe pro Jahr ============================================
@callback(
    Output("snow-max-per-year", "figure"),
    Input("snow-data-store", "data"),
    Input("snow-analysis-options", "value"),
)
def update_max_snow_per_year(all_data, options):
    """Shows maximum snow depth per year"""
    if not all_data:
        return {"data": [], "layout": {"title": "No Data"}}
    
    # Determine common time range?
    common_start = None
    common_end = None
    
    if "common_timerange" in options:
        for filename, data in all_data.items():
            df = pd.DataFrame(data["df"])
            x_col = data["x_column"]
            df[x_col] = pd.to_datetime(df[x_col], errors='coerce')
            
            if common_start is None and common_end is None:
                common_start = df[x_col].min()
                common_end = df[x_col].max()
            else:
                common_start = max(common_start, df[x_col].min())
                common_end = min(common_end, df[x_col].max())
    
    fig = go.Figure()
    
    for filename, data in all_data.items():
        df = pd.DataFrame(data["df"])
        x_column = data["x_column"]
        df[x_column] = pd.to_datetime(df[x_column])
        
        # Filter common time range
        if common_start is not None and common_end is not None:
            df = df[(df[x_column] >= common_start) & (df[x_column] <= common_end)]
        
        # Maximum snow depth per year
        max_snow_per_year = df.groupby("year")["SCHNEEHOEHE"].max()
        
        fig.add_trace(go.Bar(
            x=max_snow_per_year.index,
            y=max_snow_per_year.values,
            name=filename
        ))
    
    title = "Maximum Snow Depth per Year"
    if "common_timerange" in options and common_start and common_end:
        title += f" ({common_start.year} - {common_end.year})"
    
    fig.update_layout(
        title=title,
        xaxis={"title": "Year"},
        yaxis={"title": "Snow Depth (cm)"},
        template="plotly_white",
        barmode='group'
    )
    
    return fig
