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


def bin_by_date(twitter_info: dict, key: str):
    bins = {}
    for d, x in twitter_info.items():
        bins[d] = create_binned_lists(x[key])
    return bins


def create_binned_lists(info: dict, no_bins=6.0):
    interval = 100.0 / float(no_bins)
    bins = {}
    i = 0
    while i < 100:
        bins[i] = []
        for x, y in info.items():
            if i + interval >= y > i:
                bins[i].append(x)
        i += interval
    return bins


def create_similarity_dict(xs, ys) -> Dict[str, float]:
    sim = {}
    for x, fx in xs:
        for y, fy in ys:
            if x == y:
                sim[x] = np.abs(fx - fy)
    # At this point, the lower the score the higher the match
    if len(sim) == 0:
        return sim
    a = min(sim.values())
    b = max(sim.values())
    for x, y in sim.items():
        # Flip the match and make it from 0-100
        sim[x] = (1.0 - ((y - a) / (b - a))) * 100
    return dict(sorted(sim.items(), key=lambda i: i[1], reverse=True))


def create_sentiment_graph(twitter_info: dict, media_info: dict):
    return dcc.Graph(
        id='sentiment-graph',
        figure=go.Figure(
            layout={
                'title': 'Twitter vs Media Sentiment',
                'xaxis_title': "Date",
                'yaxis_title': "Sentiment",
            },
            data=[
                go.Scatter(
                    name='Twitter Sentiment',
                    x=list(twitter_info.keys()),
                    y=[x['sentiment'].mean() for x in twitter_info.values()],
                    error_y=dict(
                        array=[x['sentiment'].std() for x in twitter_info.values()],
                        visible=True)
                ),
                go.Scatter(
                    name='Media Sentiment',
                    x=list(media_info.keys()),
                    y=[x['sentiment'].mean() for x in media_info.values()],
                    error_y=dict(
                        array=[x['sentiment'].std() for x in media_info.values()],
                        visible=True)
                )
            ]
        )
    )


def create_similarity_graph(twitter_info: dict, media_info: dict):
    similarity_info = {
        'key_phrases': [],
        'emotional_traits': [],
        'behavioral_traits': []
    }
    for key in similarity_info.keys():
        for d in twitter_info.keys():
            sims = np.nanmean(
                list(create_similarity_dict(twitter_info[d][key].items(), media_info[d][key].items()).values()))
            similarity_info[key].append(np.nan_to_num(sims))
    return dcc.Graph(
        id='sim-graph',
        figure=go.Figure(
            layout={
                'title': 'Key Phrases and Trait Similarity',
                'xaxis_title': "Date",
                'yaxis_title': "Similarity",
            },
            data=[
                go.Scatter(
                    name='Key Phrases',
                    x=list(twitter_info.keys()),
                    y=similarity_info['key_phrases']
                ),
                go.Scatter(
                    name='Emotional Traits',
                    x=list(twitter_info.keys()),
                    y=similarity_info['emotional_traits']
                ),
                go.Scatter(
                    name='Behavioral Traits',
                    x=list(twitter_info.keys()),
                    y=similarity_info['behavioral_traits']
                )
            ]
        )
    )


def create_word_lists(twitter_info: dict, media_info: dict, key: str):
    iter_obj = []
    for d in twitter_info.keys():
        iter_obj.append((d, twitter_info[d][key].items(), media_info[d][key].items()))

    def make_list_item(text: str, freq: float):
        if freq > 80:
            col = "danger"
        elif 80 >= freq > 60:
            col = "warning"
        elif 60 >= freq > 40:
            col = "success"
        elif 40 >= freq > 20:
            col = "info"
        else:
            col = "secondary"
        return dbc.ListGroupItem(text, color=col)

    if key == "key_phrases":
        title = "Key Phrases"
    elif key == "emotional_traits":
        title = "Emotional Traits"
    else:
        title = "Behavioral Traits"

    return [
        dbc.Tab(
            label="{}-05".format(dt.datetime.fromisoformat(d).day),
            children=[
                dbc.Card([
                    dbc.CardBody([
                        html.H4(title, className="card-title text-center"),
                        dbc.Row([
                            dbc.Col(width="4",
                                    children=[html.H5("Twitter", className="text-center"),
                                              dbc.ListGroup([make_list_item(x, f) for x, f in xs], flush=True)]
                                    ),
                            dbc.Col(width="4",
                                    children=[html.H5("Matches", className="text-center"),
                                              dbc.ListGroup([make_list_item(z, f)
                                                             for z, f in create_similarity_dict(xs, ys).items()],
                                                            flush=True)]
                                    ),
                            dbc.Col(width="4",
                                    children=[html.H5("Media", className="text-center"),
                                              dbc.ListGroup([make_list_item(y, f) for y, f in ys], flush=True)]
                                    ),
                        ], justify="center", )
                    ], style={"maxHeight": "400px", "overflow": "scroll"}
                    ),
                ]),
            ]
        )
        for d, xs, ys in iter_obj
    ]


def create_wordcloud_tabs(twitter_info: dict, media_info: dict, key: str):
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
                ),
                dbc.CardHeader("Media"),
                dbc.CardBody(
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='media-{}-{}-wordcloud'.format(key, d),
                                          figure=plotly_wordcloud(y[key])), width="12", lg="auto"),
                        dbc.Col([
                            html.H5("Top Results"),
                            html.Ul(
                                [html.Li("{}".format(phrase, p)) for phrase, p in
                                 list(sorted(y[key].items(), key=lambda item: item[1], reverse=True))[:15]]
                            )]
                            , width="4")
                    ]),
                ),
            ],
                className="mt-2",
            ),
            label="{}-05".format(dt.datetime.fromisoformat(d).day)
        )
        for (d, x), y in zip(twitter_info.items(), media_info.values())
    ]
