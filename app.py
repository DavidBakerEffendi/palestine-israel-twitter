import random
from typing import Dict

import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import json
import nltk
from nltk.corpus import stopwords
import config as conf

import components
import config
from scraping import import_tweets
import text

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

tags = []
tags.extend([("n", x) for x in import_tweets.get_hashtags(conf.NEUTRAL_HASHTAGS)])
tags.extend([("i", x) for x in import_tweets.get_hashtags(conf.PRO_ISRAEL_HASHTAGS)])
tags.extend([("p", x) for x in import_tweets.get_hashtags(conf.PRO_PALESTINE_HASHTAGS)])
random.shuffle(tags)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stop_words = set(stopwords.words('english'))


def df_by_date(df_to_sort) -> Dict[str, Dict[str, any]]:
    dict_by_date = {}
    for d, g in df_to_sort.sort_values(['date']).groupby('date'):
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
            all_kps[k] = np.mean(v)
        for kps in g['emotional_traits']:
            for k, v in kps.items():
                if k not in e_traits.keys():
                    e_traits[k] = [v]
                else:
                    e_traits[k].append(v)
        for k, v in e_traits.items():
            e_traits[k] = np.mean(v)
        for kps in g['behavioral_traits']:
            for k, v in kps.items():
                if k not in b_traits.keys():
                    b_traits[k] = [v]
                else:
                    b_traits[k].append(v)
        for k, v in b_traits.items():
            b_traits[k] = np.mean(v)

        kp_entry = dict(sorted(all_kps.items(), key=lambda item: item[1], reverse=True))
        e_entry = dict(sorted(e_traits.items(), key=lambda item: item[1], reverse=True))
        b_entry = dict(sorted(b_traits.items(), key=lambda item: item[1], reverse=True))

        dict_by_date[d] = {
            "sentiment": g['sentiment'],
            "key_phrases": kp_entry,
            "emotional_traits": e_entry,
            "behavioral_traits": b_entry
        }
    return dict_by_date


def make_tag_item(af, tag):
    body = dbc.CardBody(html.P(tag, className="card-text"))
    if af == "n":
        return dbc.Card(body, color="secondary", className="mb-2", inverse=True)
    elif af == "p":
        return dbc.Card(body, color="primary", className="mb-2", inverse=True)
    else:
        return dbc.Card(body, color="info", className="mb-2", inverse=True)


twitter_info = df_by_date(twitter_df)
media_info = df_by_date(media_df)

app.layout = html.Div(children=[
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("David Baker Effendi", href="https://davidbakereffendi.github.io")),
        ],
        brand="Sentiment & Opinion Mining: 2021 Israel–Palestine Crisis",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dbc.Container(children=[
        dbc.Alert(children=[
            "This project is an entry to the expert.ai 2021 ",
            html.A("Sentiment & Opinion Mining Natural Language API Hackathon",
                   href="https://expertai-nlapi-042021.devpost.com"),
            """
            . The goal is to better understand the relationship between the public reaction and media portrayal of 
            the 2021 Israel-Palestine Crisis. The project code is open-source and can be found on
            """,
            html.A("GitHub", href="https://github.com/DavidBakerEffendi/palestine-israel-twitter"),
            ". The GitHub also contains the URLs used to scrape media article data from and be seen as the references "
            "used for the information stated in the introduction paragraph."
        ],
            color="info",
            style={'margin': '2em 0em 1em 0em'}
        ),
        html.H2(children='Introduction'),
        html.P(text.introduction_summary),
        html.H3("The Conflict of May 2021"),
        *[html.P(children=x) for x in text.introduction_conflict_1],
        dbc.Row([
            dbc.Col(width="0", lg="1"),
            dbc.Col([
                dbc.Card(
                    dbc.CardImg(
                        src="https://ichef.bbci.co.uk/news/976/cpsprodpb/B64F/production/_118517664_gettyimages-1232873479.jpg",
                        top=True,
                        className='align-self-center',
                        style={"height": "25rem"},
                    ),
                ),
                html.P("Iron Dome defense system (L) intercepts rockets (R) fired by Hamas on 10 May. (Photo by ANAS"
                       " BABA/AFP via Getty Images)", className="card-footer")
            ], width="12", lg="10"),
            dbc.Col(width="0", lg="1"),
        ]),
        *[html.P(children=x) for x in text.introduction_conflict_2],
        html.H3("Problem Statement"),
        *[html.P(children=x) for x in text.introduction_problem],
        html.H2(children='Method'),
        *[html.P(children=x) for x in text.method_summary],
        html.H3(children="Data Mining and Pre-Processing"),
        *[html.P(children=x) for x in text.data_mining],
        html.H4(children="Twitter Data"),
        *[html.P(children=x) for x in text.twitter_mining_1],
        dbc.Container(
            dbc.Row([
                dbc.Col(make_tag_item(af, x), width="3")
                for af, x in tags
            ]),
            style={"maxHeight": "400px", "overflow": "scroll"},
            className="mb-4 p-0"
        ),
        *[html.P(children=x) for x in text.twitter_mining_2],
        html.H4(children="Media Articles"),
        *text.media_mining,
        html.H3(children="Language Processing"),
        *[html.P(children=x) for x in text.language_processing],
        html.H2(children='Results'),
        *[html.P(children=x) for x in text.results_summary],
        html.H3(children='Sentiment Analysis'),
        *[html.P(children=x) for x in text.sentiment_paragraph],
        components.create_sentiment_graph(twitter_info, media_info),
        html.H3(children='Key Phrases and Traits'),
        *[html.P(children=x) for x in text.phrases_trait_summary],
        html.Span("Legend", className="h5"),
        html.P(
            """Each list is ordered and colored by the impact of the item on a scale of 0-100. The 
            center list is scored by how similarly impactful the item was between both datasets.
            """),
        dbc.ListGroup([
            dbc.ListGroupItem(">= 100", color="danger"),
            dbc.ListGroupItem("60-80", color="warning"),
            dbc.ListGroupItem("40-60", color="success"),
            dbc.ListGroupItem("20-40", color="info"),
            dbc.ListGroupItem("< 20", color="secondary"),
        ], horizontal=True, className="mb-2"),
        *[html.P(children=x) for x in text.key_phrases_paragraph],
        dbc.Tabs(components.create_word_lists(twitter_info, media_info, 'key_phrases')),
        *[html.P(children=x) for x in text.e_traits_paragraph],
        dbc.Tabs(components.create_word_lists(twitter_info, media_info, 'emotional_traits')),
        *[html.P(children=x) for x in text.b_traits_paragraph],
        dbc.Tabs(components.create_word_lists(twitter_info, media_info, 'behavioral_traits')),
        *[html.P(children=x) for x in text.sim_paragraph],
        components.create_similarity_graph(twitter_info, media_info),
        html.H2(children='Conclusion'),
        *[html.P(children=x) for x in text.conclusion],
        html.H2(children='Future Work'),
        *[html.P(children=x) for x in text.future_work],
        dbc.Alert(children=[
            html.P("I would like to give a special thanks to those who made this project possible:"),
            html.Ul([
                html.Li("Expert.ai for hosting the hackathon and raising the free-tier limit to allow me to be able to "
                        "process the large quantities of data mined."),
                html.Li("To Twitter for providing me with access to the academic research product track so that I "
                        "was able to mine tweets from this time period."),
                html.Li(["My partner, ", html.A("Lauren Hayward",
                                                href="https://www.linkedin.com/in/lauren-hayward-8ba853199/"),
                        ", for the idea for this project and the time spent proof-reading my work."])
            ])
        ],
            color="info",
            style={'margin': '2em 0em 1em 0em'}
        ),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=config.DEBUG, host=config.HOST, port=config.PORT)
