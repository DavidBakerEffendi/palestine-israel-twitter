from typing import Dict, List
import datetime as dt
import config as conf
import requests
import time
import json

URL = "https://api.twitter.com/2"
REQUEST_CAP = 450
REQUEST_WINDOW = 15 * 60.0  # 15 minute window
SECONDS_PER_REQUEST = (REQUEST_WINDOW + 1) / REQUEST_CAP  # Add a bit of slack
MAX_RESULTS = 10


def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(conf.TWITTER_BEARER_TOKEN)
    }


def get(endpoint: str, params: Dict):
    return requests.get("{}/{}".format(URL, endpoint), params=params, headers=headers()).json()


def pull_data(file_pref, query):
    flag = False
    i = 0
    next_token = None
    while not flag:
        if conf.DEBUG:
            print("Query {}".format(i))
        res = get_recent_tweets(query, next_token)
        result_count = int(res['meta']['result_count'])
        users = res['includes']['users']
        next_token = res['meta']['next_token']
        tweets = res['data']

        write_to_file('{}_tweets.txt'.format(file_pref), tweets)
        write_to_file('users.txt', users)

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
        'start_time': (dt.datetime.now() - dt.timedelta(days=6.9999)).astimezone().isoformat(),
        'end_time': (dt.datetime.now() - dt.timedelta(seconds=10)).astimezone().isoformat(),
        'expansions': 'author_id,geo.place_id',
        'place.fields': 'country',
        'user.fields': 'id,location,verified'
    }
    if next_token is not None:
        params['next_token'] = next_token
    return get("tweets/search/recent", params)


def get_hashtags(f_name: str) -> List[str]:
    with open(f_name, 'r') as f:
        return f.read().splitlines()


def write_to_file(f_name: str, input_list: List[str]):
    with open(f_name, 'a+') as f:
        for i in input_list:
            f.write(json.dumps(i) + "\n")


if __name__ == "__main__":
    # result = get("tweets/search/recent", {
    #     'query': 'from:TwitterDev',
    #     'tweet.fields': 'created_at',
    #     'expansions': 'author_id',
    #     'user.fields': 'created_at'
    # })
    for tag in get_hashtags(conf.NEUTRAL_HASHTAGS):
        pull_data("neutral", tag)
    for tag in get_hashtags(conf.PRO_ISRAEL_HASHTAGS):
        pull_data("pro_israel", tag)
    for tag in get_hashtags(conf.PRO_PALESTINE_HASHTAGS):
        pull_data("pro_palestine", tag)
    # print(SECONDS_PER_REQUEST)
    # print(pull_data('#HopeToGaza'))
