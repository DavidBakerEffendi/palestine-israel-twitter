from typing import Dict

import config as conf
import requests

URL = "https://api.twitter.com/2"


def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(conf.TWITTER_BEARER_TOKEN)
    }


def get(endpoint: str, params: Dict):
    return requests.get("{}/{}".format(URL, endpoint), params=params, headers=headers()).json()


if __name__ == "__main__":
    result = get("tweets/search/recent", {
        'query': 'from:TwitterDev',
        'tweet.fields': 'created_at',
        'expansions': 'author_id',
        'user.fields': 'created_at'
    })
    print(result)
