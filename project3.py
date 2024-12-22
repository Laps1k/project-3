import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
from weather_analyzer import get_weather_forecast

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Погода"),
    dcc.Input(id="cities_input", type="text", placeholder="Города через ,"),
    dcc.Dropdown(
        id="parameter-dropdown",
        options=[
            {"label":"Температура","value":"temperature"},
            {"label":"Осадки","value":"precipitation"},
            {"label":"Скорость ветра","value":"wind_speed"}
        ],
        value="temperature", clearable=False
    ),
    dcc.Dropdown(
        id="forecast-mode",
        options=[{"label":"1 день","value":1},{"label":"5 дней","value":5}],
        value=5, clearable=False
    ),
    html.Button("Построить", id="submit_button"),
    html.Div(id="error_message", style={"color":"red"}),
    dcc.Graph(id="graph"),
    html.H3("Таблица прогноза"),
    html.Div(id="table-container")
])

@app.callback(
    [Output("graph","figure"), Output("table-container","children"), Output("error_message","children")],
    [Input("submit_button","n_clicks"), Input("parameter-dropdown","value"), Input("forecast-mode","value")],
    [State("cities_input","value")]
)
def update(n_clicks, param, mode, cities_str):
    if not cities_str:
        return dash.no_update, dash.no_update, "Введите хотя бы один город!"
    cities = [x.strip() for x in cities_str.split(",") if x.strip()]
    data = []
    for city in cities:
        f = get_weather_forecast(city, interval=mode)
        for e in f["forecast"]:
            data.append({
                "city": city, "date": e["date"],
                "temperature": e["temperature"],
                "precipitation": e.get("precipitation_probability", 0),
                "wind_speed": e.get("wind_speed_kmh", 0)
            })
    df = pd.DataFrame(data)

    if mode == 1:
        if param == "precipitation":
            fig = px.bar(df, x="city", y=param, color="city", title="Осадки (1 день)")
        else:
            fig = px.bar(df, x=param, y="city", color="city", orientation='h', title="Прогноз на 1 день")
    else:
        fig = px.line(df, x="date", y=param, color="city", markers=True, title="Прогноз на 5 дней")

    pvt = df.pivot(index="date", columns="city", values=param).reset_index().rename(columns={"date": "Дата"})
    tbl = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in pvt.columns],
        data=pvt.to_dict("records"),
        style_cell={"textAlign":"center"}
    )
    return fig, tbl, ""

if __name__ == "__main__":
    app.run_server(debug=True)
