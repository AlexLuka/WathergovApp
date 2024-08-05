import plotly.graph_objects as go


def get_ts_figure(x: list, y: list):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines+markers'
        )
    )

    fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig
