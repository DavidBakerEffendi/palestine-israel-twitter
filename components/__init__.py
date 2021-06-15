import plotly as py
import plotly.graph_objs as go
import random

from typing import Dict


def plotly_wordcloud(words: Dict[str, int]):
    lower, upper = 15, 45
    frequency = [((x - min(words.values())) / (max(words.values()) - min(words.values()))) * (upper - lower) + lower
                 for x in words.values()]

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
    )
    padding = 0.3
    fig = go.Figure(
        data=[data],
        layout=layout,
        layout_yaxis_range=[min(ys) - padding, max(ys) + padding],
        layout_xaxis_range=[min(xs) - padding, max(xs) + padding]
    )

    return fig
