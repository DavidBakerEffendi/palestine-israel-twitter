import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import json

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


media_df = import_data("analyzed_media.json")
twitter_df = import_data("analyzed_tweets.json")

twitter_mean = {}
twitter_stderr = {}
for d, g in twitter_df.sort_values(['date']).groupby('date'):
    twitter_mean[d] = g['sentiment'].mean()
    twitter_stderr[d] = g['sentiment'].std()

# https://plotly.com/python/continuous-error-bars/

sentiment_graph = dcc.Graph(
    id='example-graph',
    figure={
        'data': [
            {'x': media_df['date'], 'y': media_df['sentiment'], 'type': 'line', 'name': 'Media Sentiment'},
            {'x': list(twitter_mean.keys()),
             'y': list(twitter_mean.values()),
             'y-err': list(twitter_stderr.values()),
             'type': 'line',
             'name': 'Twitter Sentiment'},
        ],
        'layout': {
            'title': 'Twitter vs Media Sentiment'
        }
    }
)

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
        the ongoing Israeli-Palestinian conflict over the Gaza strip. The vector that began the ' main events of 
        May\'s crisis was on May 6 when a group of Palestinians began to protest in East Jerusalem. This was in 
        response to the trial happening in the Supreme Court of Israel on the eviction of six Palestinian families in 
        Sheikh Jarrah.
        """),
        sentiment_graph,
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
