# app.py – Tableau de bord Dash compact (<100 lignes)

import numpy as np, pandas as pd
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px

# ---- Génération d'un petit jeu de données ----
def make_data():
    dates = pd.date_range(datetime.today()-timedelta(300), periods=300)
    cats = ["Électronique","Maison","Sport"]
    data = []
    for d in dates:
        for c in cats:
            q = np.random.randint(5, 50)
            p = np.random.uniform(10, 200)
            data.append([d.date(), c, q, p, q*p])
    return pd.DataFrame(data, columns=["Date","Catégorie","Quantité","Prix","CA"])

df = make_data()

# ---- Application ----
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Dashboard Ventes — Version courte"),

    dcc.DatePickerRange(
        id="dates", start_date=df["Date"].min(), end_date=df["Date"].max(),
        display_format="DD/MM/YYYY"
    ),

    dcc.Dropdown(
        id="cat", multi=True, placeholder="Catégories",
        options=[{"label": c, "value": c} for c in df["Catégorie"].unique()]
    ),

    html.Div(id="kpi", style={"display":"flex","gap":"25px","marginTop":"10px"}),

    dcc.Graph(id="fig", style={"height":"380px"}),

    dash_table.DataTable(id="table", page_size=10, style_table={"overflowX":"auto"})
])

# ---- Callbacks ----
@app.callback(
    Output("kpi","children"), Output("fig","figure"), Output("table","data"),
    Input("dates","start_date"), Input("dates","end_date"), Input("cat","value")
)
def update(start, end, cats):
    d = df[(df["Date"]>=pd.to_datetime(start).date()) &
           (df["Date"]<=pd.to_datetime(end).date())]
    if cats: d = d[d["Catégorie"].isin(cats)]

    # KPIs
    kpi1 = html.Div([html.B("CA total : "), f"{d['CA'].sum():,.0f} €"])
    kpi2 = html.Div([html.B("Quantité : "), f"{d['Quantité'].sum():,.0f}"])
    kpi3 = html.Div([html.B("Panier moyen : "), f"{d['CA'].mean():.1f} €"])

    # Graphique simple CA par date
    fig = px.line(d.groupby("Date")["CA"].sum().reset_index(),
                  x="Date", y="CA", title="CA par jour")

    return [kpi1, kpi2, kpi3], fig, d.to_dict("records")


if __name__ == "__main__":
    app.run(debug=True)