from typing import Set

import pandas as pd
import json

from analysis import expert_ai_api


def import_data():
    media = {}
    with open("./media.json", "r") as f:
        for line in f.readlines():
            d = json.loads(line)
            for (k, v) in d.items():
                if k not in media.keys():
                    media[k] = [v]
                else:
                    media[k].append(v)
    return pd.DataFrame(media)


def get_existing_ids() -> Set[str]:
    out = set()
    with open("./analyzed_media.json", "r+") as f:
        for line in f.readlines():
            d = json.loads(line)
            out.add(d["url"])
    return out


if __name__ == "__main__":
    df = import_data()
    expert_ai_api.check_dependencies()
    expert_ai_api.publish_credentials()

    results_by_date = {}
    grps_by_date = df.groupby(["date"])

    existing = get_existing_ids()
    for date, group in grps_by_date:
        expert_ai_api.publish_credentials()
        print("Processing data for {}".format(date))
        i = 1
        results_by_date[str(date)] = []
        print("Processing row: ", end="")
        for _, row in group.iterrows():
            if row["url"] not in existing:
                print("{}".format(i), end="...")
                i += 1
                sent, phrases, e_traits, b_traits = expert_ai_api.analyze_text(row['text'])
                results_by_date[str(date)].append({
                    'url': row['url'],
                    'sentiment': sent,
                    'key_phrases': phrases,
                    'emotional_traits': e_traits,
                    'behavioral_traits': b_traits
                })

    with open('../analyzed_media.json', 'a+') as f:
        for date, results in results_by_date.items():
            for r in results:
                d = {'date': str(date)}
                for k, v in r.items():
                    d[k] = v
                f.write(json.dumps(d) + "\n")
