import numpy as np
import plotly as py
import plotly.graph_objs as go
import random
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import datetime as dt

from typing import Dict


def plotly_wordcloud(words: Dict[str, int]):
    lower, upper = 15, 45
    frequency = [((x - min(words.values())) / (max(words.values()) - min(words.values()))) * (upper - lower) + lower
                 for x in words.values()]

    if np.isnan(np.sum(frequency)):
        frequency = [100]

    percent = list(map(lambda x: x / sum(frequency), frequency))

    length = len(words.keys())
    colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for _ in range(length)]

    xs = list(range(length))
    ys = random.choices(range(length), k=length)

    data = go.Scatter(
        x=xs,
        y=ys,
        mode='text',
        text=list(words.keys()),
        hovertext=['{0} ({1})'.format(w, format(p, '.2%')) for w, _, p in zip(words, frequency, percent)],
        hoverinfo='text',
        textfont={'size': frequency, 'color': colors}
    )
    layout = go.Layout({
        'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}
    },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        margin={'t': 0.5, 'b': 0.5, 'l': 0, 'r': 0},
    )
    padding = 0.3
    fig = go.Figure(
        data=[data],
        layout=layout,
        layout_yaxis_range=[min(ys) - padding, max(ys) + padding],
        layout_xaxis_range=[min(xs) - padding, max(xs) + padding]
    )

    return fig


def create_wordcloud_tabs(twitter_info: dict, key: str):
    return [
        dbc.Tab(
            dbc.Card([
                dbc.CardHeader("Twitter"),
                dbc.CardBody(
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='twitter-{}-{}-wordcloud'.format(key, d),
                                          figure=plotly_wordcloud(x[key])), width="12", lg="auto"),
                        dbc.Col([
                            html.H5("Top Results"),
                            html.Ul(
                                [html.Li("{}".format(phrase, p)) for phrase, p in
                                 list(sorted(x[key].items(), key=lambda item: item[1], reverse=True))[:15]]
                            )]
                            , width="4")
                    ]),
                )],
                className="mt-2",
            ),
            label="{}-05".format(dt.datetime.fromisoformat(d).day)
        )
        for d, x in twitter_info.items()
    ]