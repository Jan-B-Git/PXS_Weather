import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__)

# Read and prepare the data Arberg
df_A = pd.read_csv('data/Arber.csv', sep=',\s*', engine='python')  # handle spaces after comma
df_A.columns = df_A.columns.str.strip()  # remove whitespace from column names
df_A['DATE'] = pd.to_datetime(df_A['DATE'], format='%d.%m.%Y')
df_A = df_A.replace(-999, pd.NA)
#df_desc=df['DATE']
#prepare table
df_A_numeric=df_A.copy()
for col in df_A.columns:
    if col != 'DATE':
        df_A_numeric[col] = pd.to_numeric(df_A[col], errors='raise')
df_A_desc=df_A_numeric.drop(columns=['DATE','MESS_DATUM','LUFTTEMP_AM_ERDB_MINIMUM','WINDSPITZE_MAXIMUM','SCHNEEHOEHE','QUALITAETS_NIVEAU','DAMPFDRUCK','BEDECKUNGSGRAD','WINDGESCHWINDIGKEIT','SONNENSCHEINDAUER'])
df_A_desc_all = df_A_desc.describe(include='all')
df_A_desc_all = df_A_desc_all.reset_index().rename(columns={'index': 'Statistik'})
#prepare table for describe 2015 
df_A_2015=df_A_numeric[df_A_numeric['DATE'].dt.year == 2015]
df_A_desc_2015=df_A_2015.drop(columns=['DATE','MESS_DATUM','LUFTTEMP_AM_ERDB_MINIMUM','WINDSPITZE_MAXIMUM','SCHNEEHOEHE','QUALITAETS_NIVEAU','DAMPFDRUCK','BEDECKUNGSGRAD','WINDGESCHWINDIGKEIT','SONNENSCHEINDAUER'])
df_A_desc_2015 = df_A_desc_2015.describe(include='all')
df_A_desc_2015 = df_A_desc_2015.reset_index().rename(columns={'index': 'Statistik'})


# Read and prepare the data Straubing
df_St = pd.read_csv('data/Straubing.csv', sep=',\s*', engine='python')  # handle spaces after comma
df_St.columns = df_St.columns.str.strip()  # remove whitespace from column names
df_St['DATE'] = pd.to_datetime(df_St['DATE'], format='%d.%m.%Y')
df_St = df_St.replace(-999, pd.NA)
#prepare table 
df_St_numeric=df_St.copy()
for col in df_St.columns:
    if col != 'DATE':
        df_St_numeric[col] = pd.to_numeric(df_St[col], errors='raise')
df_St_desc=df_St_numeric.drop(columns=['DATE','MESS_DATUM','LUFTTEMP_AM_ERDB_MINIMUM','WINDSPITZE_MAXIMUM','SCHNEEHOEHE','QUALITAETS_NIVEAU','DAMPFDRUCK','BEDECKUNGSGRAD','WINDGESCHWINDIGKEIT','SONNENSCHEINDAUER'])
df_St_desc_all = df_St_desc.describe(include='all')
df_St_desc_all = df_St_desc_all.reset_index().rename(columns={'index': 'Statistik'})
#prepare table for describe 2015 
df_St_2015=df_St_numeric[df_St_numeric['DATE'].dt.year == 2015]
df_St_desc_2015=df_St_2015.drop(columns=['DATE','MESS_DATUM','LUFTTEMP_AM_ERDB_MINIMUM','WINDSPITZE_MAXIMUM','SCHNEEHOEHE','QUALITAETS_NIVEAU','DAMPFDRUCK','BEDECKUNGSGRAD','WINDGESCHWINDIGKEIT','SONNENSCHEINDAUER'])
df_St_desc_2015 = df_St_desc_2015.describe(include='all')
df_St_desc_2015 = df_St_desc_2015.reset_index().rename(columns={'index': 'Statistik'})


# Read and prepare the data Schorndorf
df_Sc = pd.read_csv('data/Schorndorf.csv', sep=',\s*', engine='python')  # handle spaces after comma
df_Sc.columns = df_Sc.columns.str.strip()  # remove whitespace from column names
df_Sc['DATE'] = pd.to_datetime(df_Sc['DATE'], format='%d.%m.%Y')
df_Sc = df_Sc.replace(-999, pd.NA)
#prepare table
df_Sc_numeric=df_Sc.copy()
for col in df_Sc.columns:
    if col != 'DATE':
        df_Sc_numeric[col] = pd.to_numeric(df_Sc[col], errors='raise')
df_Sc_desc=df_Sc_numeric.drop(columns=['DATE','MESS_DATUM','LUFTTEMP_AM_ERDB_MINIMUM','WINDSPITZE_MAXIMUM','SCHNEEHOEHE','QUALITAETS_NIVEAU','DAMPFDRUCK','BEDECKUNGSGRAD','WINDGESCHWINDIGKEIT','SONNENSCHEINDAUER'])
df_Sc_desc_all = df_Sc_desc.describe(include='all')
df_Sc_desc_all = df_Sc_desc_all.reset_index().rename(columns={'index': 'Statistik'})
#prepare table for describe 2015 
df_Sc_2015=df_Sc_numeric[df_Sc_numeric['DATE'].dt.year == 2015]
df_Sc_desc_2015=df_Sc_2015.drop(columns=['DATE','MESS_DATUM','LUFTTEMP_AM_ERDB_MINIMUM','WINDSPITZE_MAXIMUM','SCHNEEHOEHE','QUALITAETS_NIVEAU','DAMPFDRUCK','BEDECKUNGSGRAD','WINDGESCHWINDIGKEIT','SONNENSCHEINDAUER'])
df_Sc_desc_2015 = df_Sc_desc_2015.describe(include='all')
df_Sc_desc_2015 = df_Sc_desc_2015.reset_index().rename(columns={'index': 'Statistik'})

# Careate the figure
fig = px.line(  
    df_A, 
    x='DATE', 
    y='LUFTTEMPERATUR',
    title='Temperaturverlauf Arber',
    labels={'DATE': 'Datum', 'LUFTTEMPERATUR': 'Temperatur (°C)'}
)

fig1 = px.line(  
    df_St, 
    x='DATE', 
    y='LUFTTEMPERATUR',
    title='Temperaturverlauf Straubing',
    labels={'DATE': 'Datum', 'LUFTTEMPERATUR': 'Temperatur (°C)'}
)

fig2 = px.line(  
    df_Sc, 
    x='DATE', 
    y='LUFTTEMPERATUR',
    title='Temperaturverlauf Schorndorf',
    labels={'DATE': 'Datum', 'LUFTTEMPERATUR': 'Temperatur (°C)'}
)

fig3 = px.line(  
    df_A, 
    x='DATE', 
    y='NIEDERSCHLAGSHOEHE',
    title='Niederschlagshöhe Arber',
    labels={'DATE': 'Datum', ' NIEDERSCHLAGSHOEHE': 'Liter'}
)

fig4 = px.line(  
    df_St, 
    x='DATE', 
    y='NIEDERSCHLAGSHOEHE',
    title= 'Niederschlagshöhe Straubing',
    labels={'DATE': 'Datum', ' NIEDERSCHLAGSHOEHE': 'Liter'}
)

fig5 = px.line(  
    df_Sc, 
    x='DATE', 
    y='NIEDERSCHLAGSHOEHE',
    title='Niedrschlagshöhe Schorndorf',
    labels={'DATE': 'Datum', ' NIEDERSCHLAGSHOEHE': 'Liter'}
)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3(['Trends Temperatur und Niederschlag']),
            html.P([html.B(['Temperatur'])], className='par')
        ], className='row-titles')
    ]),
    # Plot output
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="temperature-plot",
                figure=fig
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="temperature-plot",
                figure=fig1
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="temperature-plot",
                figure=fig2
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="Niederschlags-plot",
                figure=fig3
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="Niederschlags-plot",
                figure=fig4
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="Niederschlags-plot",
                figure=fig5
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("Descriptive statistics — Arber"),
            dash_table.DataTable(
                id='describe-table-arber',
                columns=[{"name": c, "id": c} for c in df_A_desc_all.columns],
                data=df_A_desc_all.to_dict('records'),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ])
    ]),
        dbc.Row([
        dbc.Col([
            html.H4("Descriptive statistics — Arber - 2015"),
            dash_table.DataTable(
                id='describe-table-arber-2015',
                columns=[{"name": c, "id": c} for c in df_A_desc_2015.columns],
                data=df_A_desc_2015.to_dict('records'),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ])
    ]),
        dbc.Row([
        dbc.Col([
            html.H4("Descriptive statistics — Straubing"),
            dash_table.DataTable(
                id='describe-table-straubing',
                columns=[{"name": c, "id": c} for c in df_St_desc_all.columns],
                data=df_St_desc_all.to_dict('records'),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ])
    ]),
            dbc.Row([
        dbc.Col([
            html.H4("Descriptive statistics — Straubing - 2015"),
            dash_table.DataTable(
                id='describe-table-straubing-2015',
                columns=[{"name": c, "id": c} for c in df_St_desc_2015.columns],
                data=df_St_desc_2015.to_dict('records'),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ])
    ]),
        dbc.Row([
        dbc.Col([
            html.H4("Descriptive statistics — Schorndorf"),
            dash_table.DataTable(
                id='describe-table-schorndorf',
                columns=[{"name": c, "id": c} for c in df_Sc_desc_all.columns],
                data=df_Sc_desc_all.to_dict('records'),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ])
    ]),
            dbc.Row([
        dbc.Col([
            html.H4("Descriptive statistics — schorndorf - 2015"),
            dash_table.DataTable(
                id='describe-table-schorndorf-2015',
                columns=[{"name": c, "id": c} for c in df_Sc_desc_2015.columns],
                data=df_Sc_desc_2015.to_dict('records'),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ])
    ]),
], fluid=True)