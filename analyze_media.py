import time
from typing import Tuple, List, Dict

import numpy as np

import pandas as pd
import json

from expertai.nlapi.common.errors import ExpertAiRequestError

import expert_ai_api


SECONDS_PER_REQUEST = 1 / 2


def import_data():
    media = {}
    with open("media.json", "r") as f:
        for line in f.readlines():
            d = json.loads(line)
            for (k, v) in d.items():
                if k not in media.keys():
                    media[k] = [v]
                else:
                    media[k].append(v)
    return pd.DataFrame(media)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def lists_to_avgs(d: Dict[str, List[float]]) -> Dict[str, float]:
    out_dict = {}
    for k in d.keys():
        out_dict[k] = float(np.mean(d[k]))
    return out_dict


def analyze_text(text: str) -> Tuple[float, Dict[str, float], Dict[str, float], Dict[str, float]]:
    sent = []
    phrases = {}
    e_traits = {}
    b_traits = {}

    for chunk in chunks(expert_ai_api.clean_text(text), 20):
        payload = " ".join(chunk)
        # Sentiment
        try:
            sent.append(expert_ai_api.obtain_sentiment(payload))
        except ExpertAiRequestError:
            print("Error sending {}".format(payload))
            time.sleep(1500)
        time.sleep(SECONDS_PER_REQUEST)
        # Key phrases
        try:
            for x in expert_ai_api.obtain_key_phrases(payload):
                if x.value in phrases.keys():
                    phrases[x.value].append(x.score)
                else:
                    phrases[x.value] = [x.score]
        except ExpertAiRequestError:
            print("Error sending {}".format(payload))
            time.sleep(1500)
        time.sleep(SECONDS_PER_REQUEST)
        # Emotional traits
        try:
            for x in expert_ai_api.obtain_traits(payload):
                if x.label in phrases.keys():
                    e_traits[x.label].append(x.score)
                else:
                    e_traits[x.label] = [x.score]
        except ExpertAiRequestError:
            print("Error sending {}".format(payload))
            time.sleep(1500)
        time.sleep(SECONDS_PER_REQUEST)
        # Behavioral traits
        try:
            for x in expert_ai_api.obtain_traits(payload, taxonomy="behavioral-traits"):
                if x.label in phrases.keys():
                    b_traits[x.label].append(x.score)
                else:
                    b_traits[x.label] = [x.score]
        except ExpertAiRequestError:
            print("Error sending {}".format(payload))
            time.sleep(1500)
        time.sleep(SECONDS_PER_REQUEST)

    phrases, e_traits, b_traits = lists_to_avgs(phrases), lists_to_avgs(e_traits), lists_to_avgs(b_traits)
    return float(np.mean(sent)), phrases, e_traits, b_traits


if __name__ == "__main__":
    df = import_data()
    expert_ai_api.check_dependencies()
    expert_ai_api.publish_credentials()

    results_by_date = {}
    grps_by_date = df.groupby(["date"])

    for date, group in grps_by_date:
        print("Processing data for {}".format(date))
        data = {
            'sentiment': [],
            'key_phrases': {},
            'emotional_traits': {},
            'behavioral_traits': {}
        }
        for _, row in group.iterrows():
            sent, phrases, e_traits, b_traits = analyze_text(row['text'])
            data['sentiment'].append(sent)
            for k, v in phrases.items():
                if k not in data['key_phrases'].keys():
                    data['key_phrases'][k] = [v]
                else:
                    data['key_phrases'][k].append(v)
            for k, v in e_traits.items():
                if k not in data['emotional_traits'].keys():
                    data['emotional_traits'][k] = [v]
                else:
                    data['emotional_traits'][k].append(v)
            for k, v in b_traits.items():
                if k not in data['behavioral_traits'].keys():
                    data['behavioral_traits'][k] = [v]
                else:
                    data['behavioral_traits'][k].append(v)

        data['sentiment'] = np.mean(data['sentiment'])
        data['key_phrases'] = lists_to_avgs(data['key_phrases'])
        data['emotional_traits'] = lists_to_avgs(data['emotional_traits'])
        data['behavioral_traits'] = lists_to_avgs(data['behavioral_traits'])
        results_by_date[str(date)] = data

    with open('analyzed_media.json', 'w+') as f:
        for date, results in results_by_date.items():
            d = results.copy()
            d['date'] = str(date)
            f.write(json.dumps(d) + "\n")
