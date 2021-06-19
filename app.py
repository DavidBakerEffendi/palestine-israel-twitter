import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import json
import nltk
from nltk.corpus import stopwords
import plotly.graph_objects as go

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

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

for d, g in twitter_df.sort_values(['date']).groupby('date'):
    if d == '2021-05-07':
        continue
    all_kps = {}
    e_traits = {}
    b_traits = {}
    for kps in g['key_phrases']:
        for k, v in kps.items():
            if '@' in k or v in stop_words or len(k) < 4:
                continue
            if k not in all_kps.keys():
                all_kps[k] = [v]
            else:
                all_kps[k].append(v)
    for k, v in all_kps.items():
        all_kps[k] = np.sum(v)
    for kps in g['emotional_traits']:
        for k, v in kps.items():
            if k not in e_traits.keys():
                e_traits[k] = [v]
            else:
                e_traits[k].append(v)
    for k, v in e_traits.items():
        e_traits[k] = np.nansum(v)
    for kps in g['behavioral_traits']:
        for k, v in kps.items():
            if k not in b_traits.keys():
                b_traits[k] = [v]
            else:
                b_traits[k].append(v)
    for k, v in b_traits.items():
        b_traits[k] = np.nansum(v)

    kp_entry = dict(sorted(all_kps.items(), key=lambda item: item[1], reverse=True)[:50])
    e_entry = dict(sorted(e_traits.items(), key=lambda item: item[1], reverse=True)[:50])
    b_entry = dict(sorted(b_traits.items(), key=lambda item: item[1], reverse=True)[:50])

    twitter_info[d] = {
        "sentiment": g['sentiment'],
        "key_phrases": kp_entry,
        "emotional_traits": e_entry,
        "behavioral_traits": b_entry
    }

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


key_phrases_tabs = components.create_wordcloud_tabs(twitter_info, 'key_phrases')
e_traits_tabs = components.create_wordcloud_tabs(twitter_info, 'emotional_traits')
b_traits_tabs = components.create_wordcloud_tabs(twitter_info, 'behavioral_traits')

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About", href="#")),
    ],
    brand="Sentiment & Opinion Mining: 2021 Israel–Palestine Crisis",
    brand_href="#",
    color="primary",
    dark=True,
)

introduction = [
    """
    On May 10 2021 an outbreak of violence, looting, rocket attacks and protests commenced in 
    the ongoing Israeli-Palestinian conflict over the Gaza strip. The vector that began the main events of 
    May\'s crisis was on May 6 when a group of Palestinians began to protest in East Jerusalem. This was in 
    response to the trial happening in the Supreme Court of Israel on the eviction of six Palestinian families in 
    Sheikh Jarrah. This eviction is long legal battle against right-wing Jewish Israelis trying to acquire property in 
    the neighbourhood. Sheikh Jarrah is a primarily Palestinian neighbourhood but it is effectively annexed by Israel 
    and under military control. 
    """,
    """
    
    """
]

app.layout = html.Div(children=[
    navbar,
    dbc.Container(children=[
        dbc.Alert(
            "This project is written to be as unbiased as possible and to simply present the facts. The events in this "
            "piece are recent and the pain may still be raw for some. This is both educational and should provide "
            "some interesting insights to how mainstream media and Twitter users react to the events of the 2021 "
            "Israel–Palestine crisis.",
            color="primary",
            style={'margin': '2em 0em 1em 0em'}
        ),
        html.H2(children='Introduction'),
        *[html.P(children=x) for x in introduction],
        html.H2(children='Method'),
        html.H2(children='Results'),
        html.H3(children='Sentiment Analysis'),
        sentiment_graph,
        html.H3(children='Key Phrases and Traits'),
        dbc.Tabs(key_phrases_tabs),
        dbc.Tabs(e_traits_tabs),
        dbc.Tabs(b_traits_tabs),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
