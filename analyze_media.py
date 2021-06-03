from typing import Tuple, List, Set

import numpy as np

import pandas as pd
import json
import expert_ai_api

REQUEST_CAP = 120
REQUEST_WINDOW = 60.0
SECONDS_PER_REQUEST = REQUEST_WINDOW / REQUEST_CAP


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


def analyze_text(text: str) -> Tuple[float, Set[str], Set[str], Set[str]]:
    sent = []
    phrases = set()
    e_traits = set()
    b_traits = set()
    for chunk in chunks(expert_ai_api.clean_text(text), 25):
        payload = " ".join(chunk)
        sent.append(expert_ai_api.obtain_sentiment(payload))
        phrases |= set([x.value for x in expert_ai_api.obtain_key_phrases(payload)])
        e_traits |= set([x.label for x in expert_ai_api.obtain_traits(payload)])
        b_traits |= set([x.label for x in expert_ai_api.obtain_traits(payload, taxonomy="behavioral-traits")])
    return float(np.mean(sent)), phrases, e_traits, b_traits


if __name__ == "__main__":
    df = import_data()
    expert_ai_api.check_dependencies()
    expert_ai_api.publish_credentials()

    results_by_date = {}
    grps_by_date = df.groupby(["date"])
    # for date, group in grps_by_date:
    #     for g in group.iterrows():
    #         print(g)

