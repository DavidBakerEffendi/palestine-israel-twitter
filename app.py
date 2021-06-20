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

introduction_conflict_1 = [
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
    As anger grew around the potential eviction, Palestinian youth began throwing rocks at Israeli police force from
    Jerusalem’s Al-Aqsa Mosque. Al-Aqsa Mosque is considered Islam's third holiest site and is also known as Temple 
    Mount. Hundreds of police responded with firing rubber bullets and stun grenades at thousands of Palestinians which 
    resulted in 205 Palestinians and 17 officers being injured. Already at this point had the violence drawn 
    international protests and calls for peace from world leaders.
    """,
]

introduction_conflict_2 = [
    """
    The clashes coincided with Qadr Night (8 May) and Jerusalem Day (9-10 May) observed by Muslims and Jews 
    respectively. At this point more than 700 Palestinians were injured. By 10 May Hamas, a Palestinian Sunni-Islamic 
    fundamentalist, militant, and nationalist organization, gave Israel an ultimatum to withdraw security forces from 
    Temple Mount and Sheikh Jarrah by 6PM otherwise consequences will follow. The ultimatum was not met with a response 
    and Hamas proceeded to launch rockets at Israel of which most were intercepted by Israel's Iron Dome defense system.
    Those of which managed to pass through hit residences and a school. Israel responded with multiple airstrikes 
    against Gaza demolishing buildings including schools, hospitals, and refugee camps. On 13 May Hamas first proposed a 
    ceasefire which was rejected by Israeli prime minister Benjamin Netanyahu.
    """,
    """
    The period between 10 May and the initial cease-fire on 21 May left 256 Palestinians including 66 children dead, 
    whereas Israel was left with at least 13 deaths, two of which were children. Casualties and displaced civilians were
    majority Palestinian. By 21 May a ceasefire came into effect, but this was ultimately broken on 16 June when Hamas
    launched incendiary balloons into Israel. The Israeli Air Force responded by carrying out multiple airstrikes in the 
    Gaza strip.
    """
]

introduction_problem = [
    """
    The crisis is one deeply rooted in political and religious debate in the ongoing Israeli-Palestinian conflict,
    marked as taking place since the mid-20th century. Opinions of the crisis from both sides are vocal on social media 
    followed with day-to-day mainstream media coverage. Both the mainstream media and public opinion are vulnerable to
    bias and misinformation. While bias requires more advanced context-specific techniques to analyze, we can already 
    mine sentiment and opinion.
    """,
    """
    In this project we would like to mine the sentiment, behavioural, and emotional traits from Tweets
    and articles by various media outlets. Both Twitter and media outlets produce masses of data that require 
    sophisticated processing techniques. We hope to identify: (i) Patterns which may or may not exist between the public
    and the media i.e. whether the media influences the masses or whether the media misrepresents public opinion on 
    divisive matters. (ii) Whether the media would step outside the bounds of objectivity towards an emotional response
    if pushed by mounting public pressure.
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
        html.P(["""
        The following introduction will cover both the socio-political scenario that is the 2021 Israel-Palestine crisis
        and the structure of how the resulting data from the public is processed. The introduction is then followed by
        the method and results of the processing the data using""", html.I("expert.ai"), """'s natural language 
        processing API. At the end we conclude our findings and explain potential future work on this kind of data.
        """]),
        html.H3("The Conflict of May 2021"),
        *[html.P(children=x) for x in introduction_conflict_1],
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
        *[html.P(children=x) for x in introduction_conflict_2],
        html.H3("Problem Statement"),
        *[html.P(children=x) for x in introduction_problem],
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
