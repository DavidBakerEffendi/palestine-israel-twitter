from typing import Tuple, List, Set
import re
import pandas as pd
import json

import expert_ai_api


def import_data():
    media = {}
    keys_wanted = ["author_id", "id", "created_at", "text"]
    with open("tweets.json", "r") as f:
        for line in f.readlines():
            d = json.loads(line)

            for (k, v) in d.items():
                if k in keys_wanted:
                    if k not in media.keys():
                        media[k] = [v]
                    else:
                        media[k].append(v)
    return pd.DataFrame(media)


def get_existing_ids() -> Set[str]:
    out = set()
    with open("analyzed_tweets.json", "r+") as f:
        for line in f.readlines():
            d = json.loads(line)
            out.add(d["id"])
    return out


def write_to_file(d: dict):
    with open("analyzed_tweets.json", "a+") as f:
        f.write(json.dumps(d) + "\n")


def load_tags() -> Tuple[List[str], List[str], List[str]]:
    neu = []
    pro_israel = []
    pro_palestine = []
    with open("resources/neutral.txt", "r") as f:
        for line in f.readlines():
            neu.append(line.strip())
    with open("resources/pro_israel.txt", "r") as f:
        for line in f.readlines():
            pro_israel.append(line.strip())
    with open("resources/pro_palestine.txt", "r") as f:
        for line in f.readlines():
            pro_palestine.append(line.strip())
    return neu, pro_israel, pro_palestine


def determine_bias(text: str, neu: List[str], pro_is: List[str], pro_pa: List[str]) -> (int, int, int):
    neu_bias, pro_is_bias, pro_pa_bias = 0, 0, 0
    for w in neu:
        if w in text:
            neu_bias += 1
    for w in pro_is:
        if w in text:
            pro_is_bias += 1
    for w in pro_pa:
        if w in text:
            pro_pa_bias += 1
    return pro_pa_bias, neu_bias, pro_is_bias


if __name__ == "__main__":
    df = import_data()
    expert_ai_api.check_dependencies()
    expert_ai_api.publish_credentials()
    pd.set_option('display.max_colwidth', None)

    neu, pro_is, pro_pa = load_tags()

    existing = get_existing_ids()
    for _, row in df.iterrows():
        if row["id"] not in existing:
            t = re.sub(r"RT @\w+:", "", row['text'])
            sent, phrases, e_traits, b_traits = expert_ai_api.analyze_text(t)
            pab, nb, isb = determine_bias(t, neu, pro_is, pro_pa)
            out = {
                "date": row["created_at"][:10],
                "author_id": row["author_id"],
                "id": row["id"],
                "sentiment": sent,
                "key_phrases": phrases,
                "emotional_traits": e_traits,
                "behavioral_traits": b_traits,
                "bias": [pab, nb, isb]
            }
            write_to_file(out)
