import datetime

import arrow
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import influxdb
import plotly.graph_objects as go

import config


app = dash.Dash(__name__)

AGGREGATION_DURATIONS = [5, 10, 20]
AGGREGATION_METHODS = ["min", "max", "median"]
REFRESHING_DURATIONS = ["5s", "10s", "30s", "1m", "5m"]

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Date:"),
                dcc.DatePickerSingle(
                    id="selected-date-variable",
                    date=datetime.date.today(),
                    max_date_allowed=datetime.date.today(),
                    display_format="MMM Do, YYYY",
                ),
            ],
        ),
        dbc.FormGroup(
            [
                dbc.Label("Refreshing every:"),
                dcc.Dropdown(
                    id="refresh-duration-variable",
                    options=[
                        {"label": duration, "value": duration}
                        for duration in REFRESHING_DURATIONS
                    ],
                    clearable=False,
                    value=REFRESHING_DURATIONS[-1],
                ),
            ],
        ),
        dbc.FormGroup(
            [
                dbc.Label("Aggregation:"),
                dcc.Dropdown(
                    id="duration-variable",
                    options=[
                        {"label": f"{duration} minutes", "value": duration}
                        for duration in AGGREGATION_DURATIONS
                    ],
                    clearable=False,
                    value=AGGREGATION_DURATIONS[-1],
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Aggregation method:"),
                dcc.Dropdown(
                    id="aggregation-method-variable",
                    options=[
                        {"label": method, "value": method}
                        for method in AGGREGATION_METHODS
                    ],
                    clearable=False,
                    value="median",
                ),
            ]
        ),
    ],
    body=True,
)

app.layout = html.Div(
    dbc.Container(
        [
            html.H1("InfluxDB live data"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(controls, md=3),
                    dbc.Col(dcc.Graph(id="live-update-graph"), md=8),
                ],
                align="center",
                justify="center",
            ),
            dcc.Interval(id="interval-component"),
        ],
        fluid=True,
    ),
    className="dash-bootstrap mt-2",
)


@app.callback(
    dash.dependencies.Output("interval-component", "interval"),
    [dash.dependencies.Input("refresh-duration-variable", "value")],
)
def update_interval(refresh_duration: str) -> int:
    duration = int(refresh_duration[:-1]) * 1000
    if refresh_duration[-1] == "m":
        duration *= 60
    return duration


@app.callback(
    dash.dependencies.Output("live-update-graph", "figure"),
    [
        dash.dependencies.Input("interval-component", "n_intervals"),
        dash.dependencies.Input("duration-variable", "value"),
        dash.dependencies.Input("selected-date-variable", "date"),
        dash.dependencies.Input("aggregation-method-variable", "value"),
    ],
)
def update_graph_live(n, aggregation_duration, selected_date, aggregation_method):
    client = influxdb.DataFrameClient(database=config.DATABASE)

    start_time = arrow.get(selected_date)
    end_time = start_time + datetime.timedelta(days=1)
    measures = client.query(
        f"""
        select {aggregation_method}({config.INDICATOR}) as {config.INDICATOR} \
            from {config.MEASUREMENT} \
            where time >= '{start_time.isoformat()}' \
            and time <= '{end_time.isoformat()}' \
            group by time({aggregation_duration}m), "{config.TAG}"
        """
    )

    fig = go.Figure(
        layout=dict(legend=dict(orientation="h"), margin=dict(l=20, r=20, t=20, b=20)),
    )

    for (_, ((_, tag_value),)), data in measures.items():
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[config.INDICATOR],
                name=tag_value,
                mode="lines+markers",
            ),
        )

    return fig


if __name__ == "__main__":
    app.run_server(debug=config.DEBUG)
