from typing import Dict, List
import config as conf
import requests
import time
import json
import re

URL = "https://api.twitter.com/2"
REQUEST_CAP = 300
REQUEST_WINDOW = 15 * 60.0  # 15 minute window
SECONDS_PER_REQUEST = (REQUEST_WINDOW + 1) / REQUEST_CAP  # Add a bit of slack
MAX_RESULTS = 500
TWEETS_FILE = "./tweets.json"
USERS_FILE = "./users.json"


def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(conf.TWITTER_BEARER_TOKEN)
    }


def get(endpoint: str, params: Dict):
    return requests.get("{}/{}".format(URL, endpoint), params=params, headers=headers()).json()


def pull_data(query):
    flag = False
    i = 0
    next_token = None
    while not flag:
        if conf.DEBUG:
            print("Query {}".format(i))
        res = get_recent_tweets(query, next_token)
        result_count = int(res['meta']['result_count'])

        try:
            if result_count == MAX_RESULTS:
                next_token = res['meta']['next_token']
        except:
            print("Warning, no next token found in {}".format(res))

        try:
            tweets = res['data']
            write_to_file(TWEETS_FILE, tweets)
        except:
            print("Error while writing tweets from {}".format(res))

        try:
            users = res['includes']['users']
            write_to_file(USERS_FILE, users)
        except:
            print("Error while writing users from {}".format(res))

        if conf.DEBUG:
            print('Result count: {}'.format(result_count))
            print("Users ({}): {}".format(len(users), users))
            print("Tweets ({}): {}".format(len(tweets), tweets))
            print("Next token: {}".format(next_token))
        if result_count < MAX_RESULTS:
            flag = True
        time.sleep(SECONDS_PER_REQUEST)


def get_recent_tweets(query: str, next_token=None):
    params = {
        'query': query,
        'max_results': MAX_RESULTS,
        'expansions': 'author_id,geo.place_id',
        'place.fields': 'country',
        'user.fields': 'id,location,verified',
        'tweet.fields': 'id,created_at,geo,lang,text,withheld'
    }
    if next_token is not None:
        params['next_token'] = next_token
    if conf.TWEETS_FROM is not None:
        params['start_time'] = conf.TWEETS_FROM
    if conf.TWEETS_TO is not None:
        params['end_time'] = conf.TWEETS_TO
    return get("tweets/search/all", params)


def get_hashtags(f_name: str) -> List[str]:
    with open("./assets/{}".format(f_name), 'r') as f:
        return f.read().splitlines()


def write_to_file(f_name: str, input_collection, w_flag='a+'):
    with open(f_name, w_flag) as f:
        for i in input_collection:
            f.write(json.dumps(i) + "\n")


def dedup_datasets():
    blacklisted_authors = ["1390401696329871363"]
    with open(TWEETS_FILE, 'r') as f:
        l = {}
        for line in f.readlines():
            skip = False
            # Some authors just post noise
            for a in blacklisted_authors:
                if '"author_id": "{}"'.format(a) in line:
                    skip = True
            if skip:
                continue
            j = json.loads(remove_unicode(line))
            if j["lang"] != "en":
                skip = True
            if not skip:
                l[j["id"]] = j
    write_to_file(TWEETS_FILE, l.values(), 'w+')
    with open(USERS_FILE, 'r') as f:
        l = {}
        for line in f.readlines():
            j = json.loads(line)
            l[j["id"]] = j
    write_to_file(USERS_FILE, l.values(), 'w+')


def remove_unicode(text):
    text = re.sub(r'\\u[\w]{4,5}', "", text).strip()
    return text


if __name__ == "__main__":
    tags = []
    tags.extend(get_hashtags(conf.NEUTRAL_HASHTAGS))
    tags.extend(get_hashtags(conf.PRO_ISRAEL_HASHTAGS))
    tags.extend(get_hashtags(conf.PRO_PALESTINE_HASHTAGS))
    for i, tag in enumerate(tags):
        print("({}/{}) Pulling data for {}".format(i + 1, len(tags), tag))
        pull_data(tag)
    dedup_datasets()
