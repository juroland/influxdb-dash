import datetime
from datetime import timezone

import dash
import dash_core_components as dcc
import dash_html_components as html
import influxdb
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import config

app = dash.Dash(__name__, external_stylesheets=config.EXTERNAL_STYLESHEETS)
app.layout = html.Div(
    html.Div(
        [
            html.H4("InfluxDB live data"),
            dcc.Graph(id="live-update-graph"),
            dcc.Interval(
                id="interval-component",
                interval=config.REFRESH_DELAY * 1000,
                n_intervals=0,
            ),
        ]
    )
)


@app.callback(
    Output("live-update-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_graph_live(n):
    client = influxdb.DataFrameClient(database=config.DATABASE)

    timestamp = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(
        seconds=config.DATA_DURATION
    )
    measures = client.query(
        f"""
        select {config.INDICATOR} from {config.MEASUREMENT} \
            where time >= '{timestamp.isoformat()}' \
            group by "{config.TAG}"
        """
    )

    fig = go.Figure()

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
