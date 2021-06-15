import numpy as np
import pandas as pd
import json

import expert_ai_api


def import_data():
    media = {}
    with open("../media.json", "r") as f:
        for line in f.readlines():
            d = json.loads(line)
            for (k, v) in d.items():
                if k not in media.keys():
                    media[k] = [v]
                else:
                    media[k].append(v)
    return pd.DataFrame(media)


if __name__ == "__main__":
    df = import_data()
    expert_ai_api.check_dependencies()
    expert_ai_api.publish_credentials()

    results_by_date = {}
    grps_by_date = df.groupby(["date"])

    for date, group in grps_by_date:
        expert_ai_api.publish_credentials()
        print("Processing data for {}".format(date))
        data = {
            'sentiment': [],
            'key_phrases': {},
            'emotional_traits': {},
            'behavioral_traits': {}
        }
        i = 1
        print("Processing row: ", end="")
        for _, row in group.iterrows():
            print("{}".format(i), end="...")
            i += 1
            sent, phrases, e_traits, b_traits = expert_ai_api.analyze_text(row['text'])
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
        print("")
        data['sentiment'] = np.mean(data['sentiment'])
        data['key_phrases'] = expert_ai_api.lists_to_avgs(data['key_phrases'])
        data['emotional_traits'] = expert_ai_api.lists_to_avgs(data['emotional_traits'])
        data['behavioral_traits'] = expert_ai_api.lists_to_avgs(data['behavioral_traits'])
        results_by_date[str(date)] = data

    with open('../analyzed_media.json', 'w+') as f:
        for date, results in results_by_date.items():
            d = {}
            for k, v in results.items():
                d[k] = v
            d['date'] = str(date)
            f.write(json.dumps(d) + "\n")
