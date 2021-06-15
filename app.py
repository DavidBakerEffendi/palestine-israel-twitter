import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import json

import components

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
EXPERT_AI_FAVICON = "https://developer.expert.ai/ui/faviconExpert.ico"


def import_data(f_name: str):
    data = {}
    with open(f_name, "r") as f:
        for line in f.readlines():
            d = json.loads(line)
            for (k, v) in d.items():
                if k == "bias":
                    continue
                if k not in data.keys():
                    data[k] = [v]
                else:
                    data[k].append(v)
    return pd.DataFrame(data)


def remove_outlier(df_in, col_name):
    """Uses z-score"""
    return df_in[((df_in[col_name] - df_in[col_name].mean()) / df_in[col_name].std()).abs() < 3]


media_df = import_data("analyzed_media.json")
twitter_df = remove_outlier(import_data("analyzed_tweets.json"), 'sentiment')


twitter_info = {}

for d, g in twitter_df.sort_values(['date']).groupby('date'):
    all_kps = {}
    for kps in g['key_phrases']:
        for k, v in kps.items():
            if '@' in k:
                continue
            if k not in all_kps.keys():
                all_kps[k] = [v]
            else:
                all_kps[k].append(v)
    for k, v in all_kps.items():
        all_kps[k] = np.mean(v)

    twitter_info[d] = {
        "sentiment": g['sentiment'],
        "key_phrases": dict(sorted(all_kps.items(), key=lambda item: item[1])[:50], reverse=True),
        "emotional_traits": {},
        "behavioral_traits": {}
    }


# https://plotly.com/python/continuous-error-bars/

import plotly.graph_objects as go

sentiment_graph = dcc.Graph(
    id='sentiment-graph',
    figure=go.Figure(
        layout={
            'title': 'Twitter vs Media Sentiment'
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
                x=media_df['date'],
                y=media_df['sentiment'],
                # error_y=dict(
                #     type='data', # value of error bar given in data coordinates
                #     array=list(twitter_stderr.values()),
                #     visible=True)
            )
        ]
    )
)


import datetime as dt

key_phrases_tabs = [
    dbc.Tab(
        dcc.Graph(id='twitter-{}-wordcloud'.format(d), figure=components.plotly_wordcloud(x['key_phrases'])),
        label="May {}".format(dt.datetime.fromisoformat(d).day)
    )
    for d, x in twitter_info.items()
]

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About", href="#")),
    ],
    brand="Sentiment & Opinion Mining: 2021 Israel–Palestine Crisis",
    brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div(children=[
    navbar,
    dbc.Container(children=[
        html.H2(children='Introduction', style={'margin': '2em 0em 1em 0em'}),
        html.P(children="""
        On May 10 2021 an outbreak of violence, looting, rocket attacks and protests commenced in 
        the ongoing Israeli-Palestinian conflict over the Gaza strip. The vector that began the main events of 
        May\'s crisis was on May 6 when a group of Palestinians began to protest in East Jerusalem. This was in 
        response to the trial happening in the Supreme Court of Israel on the eviction of six Palestinian families in 
        Sheikh Jarrah.
        """),
        sentiment_graph,
        dbc.Tabs(key_phrases_tabs),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
