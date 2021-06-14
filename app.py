import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


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

app.layout = html.Div(children=[
        html.Center(children=[
            html.H1(children='Hello Dash'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),

            sentiment_graph
        ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
