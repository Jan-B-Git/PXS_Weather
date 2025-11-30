import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

dash.register_page(__name__, path="/forecast")

def get_csv_files_from_data_folder():
    data_folder = Path("data")
    if not data_folder.exists():
        return []
    return [f.stem for f in data_folder.glob("*.csv")]

def load_temperature_csv(filename):
    data_folder = Path("data")
    filepath = data_folder / f"{filename}.csv"
    try:
        df_preview = pd.read_csv(filepath, nrows=5)
        date_col = df_preview.columns[0]
        temp_col = " LUFTTEMPERATUR"
        df = pd.read_csv(filepath, usecols=[date_col, temp_col])

        sample = str(df[date_col].iloc[0])

        if "." in sample:
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, format="%d.%m.%Y", errors="coerce")
        else:
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

        df = df.sort_values(date_col).reset_index(drop=True)
        df[temp_col] = df[temp_col].replace(-999, pd.NA)
        df = df.rename(columns={temp_col: "TEMP"})
        return df, date_col
    except:
        return None, None

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("Temperaturvorhersage"),
            dcc.Dropdown(
                id="temp-csv-selector",
                options=[],
                placeholder="Temperatur-CSV auswählen...",
                clearable=True
            )
        ], width=4),
        dbc.Col([
            dcc.Dropdown(
                id="forecast-model-selector",
                options=[
                    {"label": "OLS (T+1)", "value": "ols1"},
                    {"label": "OLS (T+3)", "value": "ols3"},
                    {"label": "Poly (T+1)", "value": "poly1"},
                    {"label": "Poly (T+3)", "value": "poly3"},
                ],
                value=["ols1", "poly1"],
                multi=True
            )
        ], width=8),
    ], className="mb-4"),
    
    dcc.Store(id="temp-data-store"),
    
    dcc.Graph(id="temp-forecast-plot", style={"height": "550px", "margin": "20px"}),
    html.Div(id="forecast-rmse-box", style={"margin": "20px"})
], fluid=True)

@callback(
    Output("temp-csv-selector", "options"),
    Input("temp-csv-selector", "id")
)
def load_temperature_options(_):
    files = get_csv_files_from_data_folder()
    return [{"label": f, "value": f} for f in files]

@callback(
    Output("temp-data-store", "data"),
    Input("temp-csv-selector", "value")
)
def load_temperature_data(filename):
    if not filename:
        return None
    df, date_col = load_temperature_csv(filename)
    if df is None:
        return None
    return {"df": df.to_dict("records"), "date_col": date_col}

@callback(
    Output("temp-forecast-plot", "figure"),
    Output("forecast-rmse-box", "children"),
    Input("temp-data-store", "data"),
    Input("forecast-model-selector", "value")
)
def forecast_temperature(data, model_selection):
    if not data:
        return go.Figure(), "Keine Daten geladen."

    df = pd.DataFrame(data["df"])
    date_col = data["date_col"]

    df["T_plus1"] = df["TEMP"].shift(-1)
    df["T_plus3"] = df["TEMP"].shift(-3)
    df = df.dropna()

    X = df[["TEMP"]].values
    y1 = df["T_plus1"].values
    y3 = df["T_plus3"].values

    split = int(len(df) * 0.8)
    X_train = X[:split]
    X_test  = X[split:]
    y1_train = y1[:split]
    y1_test  = y1[split:]
    y3_train = y3[:split]
    y3_test  = y3[split:]

    X_train_sm = sm.add_constant(X_train)
    X_test_sm  = sm.add_constant(X_test)

    olsmod_1 = sm.OLS(y1_train, X_train_sm)
    olsres_1 = olsmod_1.fit()
    olsmod_3 = sm.OLS(y3_train, X_train_sm)
    olsres_3 = olsmod_3.fit()

    y1_hat_te_ols = olsres_1.predict(X_test_sm)
    y3_hat_te_ols = olsres_3.predict(X_test_sm)

    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly  = poly.transform(X_test)

    linreg_1 = LinearRegression().fit(X_train_poly, y1_train)
    linreg_3 = LinearRegression().fit(X_train_poly, y3_train)

    y1_hat_te_poly = linreg_1.predict(X_test_poly)
    y3_hat_te_poly = linreg_3.predict(X_test_poly)

    rmse_ols_1 = mean_squared_error(y1_test, y1_hat_te_ols, squared=False)
    rmse_ols_3 = mean_squared_error(y3_test, y3_hat_te_ols, squared=False)
    rmse_poly_1 = mean_squared_error(y1_test, y1_hat_te_poly, squared=False)
    rmse_poly_3 = mean_squared_error(y3_test, y3_hat_te_poly, squared=False)

    fig = go.Figure()

    if "ols1" in model_selection:
        fig.add_trace(go.Scatter(
            x=df[date_col].iloc[split:], 
            y=y1_hat_te_ols,
            mode="lines",
            name="OLS Vorhersage (T+1)"
        ))

    if "ols3" in model_selection:
        fig.add_trace(go.Scatter(
            x=df[date_col].iloc[split:], 
            y=y3_hat_te_ols,
            mode="lines",
            name="OLS Vorhersage (T+3)"
        ))

    if "poly1" in model_selection:
        fig.add_trace(go.Scatter(
            x=df[date_col].iloc[split:], 
            y=y1_hat_te_poly,
            mode="lines",
            name="Poly Vorhersage (T+1)"
        ))

    if "poly3" in model_selection:
        fig.add_trace(go.Scatter(
            x=df[date_col].iloc[split:], 
            y=y3_hat_te_poly,
            mode="lines",
            name="Poly Vorhersage (T+3)"
        ))

    fig.add_trace(go.Scatter(
        x=df[date_col].iloc[split:], 
        y=y1_test,
        mode="lines",
        name="Echte Temperatur (T+1)",
        line=dict(color="black", width=2)
    ))

    fig.update_layout(
        title="Vorhersage der Temperatur",
        template="plotly_white",
        xaxis_title="Datum",
        yaxis_title="Temperatur (°C)",
        hovermode="x unified"
    )

    rmse_box = html.Div([
        html.H5("RMSE Ergebnisse"),
        html.P(f"OLS 1-Tag: {rmse_ols_1:.3f}"),
        html.P(f"OLS 3-Tage: {rmse_ols_3:.3f}"),
        html.P(f"Poly 1-Tag: {rmse_poly_1:.3f}"),
        html.P(f"Poly 3-Tage: {rmse_poly_3:.3f}"),
    ])

    return fig, rmse_box