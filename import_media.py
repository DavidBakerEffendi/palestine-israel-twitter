from typing import Set, List, Dict
import requests
import datetime as dt
from bs4 import BeautifulSoup as bs
import re
import calendar
import config as conf
import pickle as pk
import os.path


def read_files(path: str) -> Set[str]:
    try:
        with open(path, 'r') as f:
            return set([str(l).strip() for l in f.readlines()])
    except Exception as _:
        return set([])


def insert_new_url(d, date: dt.datetime, media: str, url: str):
    if date not in d.keys():
        d[date] = {media: [url]}
    else:
        media_dict = d[date]
        if media not in media_dict.keys():
            media_dict[media] = [url]
        else:
            media_dict[media].append(url)


def parse_dates(urls: Set[str]) -> Dict[dt.datetime, Dict[str, List[str]]]:
    out_dict = {}
    for url in urls:
        if "https://ewn.co.za/" in url:
            raw_dt = url.strip("https://ewn.co.za/")[:10].split('/')
            date = dt.datetime(int(raw_dt[0]), int(raw_dt[1]), int(raw_dt[2]))
            insert_new_url(out_dict, date, "EWN", url)
        elif "https://apnews.com/" in url:
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            for match in soup.select('span[data-key="timestamp"]'):
                gs = re.match(r"^(\w+)[ ](\d+)[, ]+(\d+).*$", match.string)
                month_num = list(calendar.month_name).index(gs.group(1))
                day_num = gs.group(2)
                year_num = gs.group(3)
                date = dt.datetime(int(year_num), int(month_num), int(day_num))
                insert_new_url(out_dict, date, "Associated Press", url)
        elif "https://www.bbc.com/" in url:
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            for match in soup.select('time[data-testid="timestamp"]'):
                gs = re.match(r"^.*datetime=\"(\d+)-(\d+)-(\d+)T.*$", str(match))
                day_num = gs.group(3)
                month_num = gs.group(2)
                year_num = gs.group(1)
                date = dt.datetime(int(year_num), int(month_num), int(day_num))
                insert_new_url(out_dict, date, "BBC", url)
        elif "https://www.theguardian.com/" in url:
            gs = re.match(r"^https://www.theguardian.com/[\w\-\/]*/(\d+)/(\w+)/(\d+)/.*$", url)
            day_num = gs.group(3)
            month_num = list(calendar.month_name).index(str(gs.group(2)).title())
            year_num = gs.group(1)
            date = dt.datetime(int(year_num), int(month_num), int(day_num))
            insert_new_url(out_dict, date, "The Guardian", url)
    return out_dict


def get_data() -> Dict[dt.datetime, Dict[str, List[str]]]:
    """
    Reads the URLs from "./resources/media_articles.txt" and organizes these by date and news outlet.
    :return a dictionary with keys being datetime and values being strings to lists of URLs.
    """
    mu_pickle = "./media_urls.pickle"
    print("Getting media objects... ", end="")
    if os.path.isfile(mu_pickle):
        with open(mu_pickle, "rb") as mu:
            out_dict = pk.load(mu)
    else:
        urls = read_files(conf.MEDIA_URLS_PATH)
        out_dict = parse_dates(urls)
        with open(mu_pickle, "wb") as mu:
            pk.dump(out_dict, mu)
    print("Success!")
    return out_dict


if __name__ == "__main__":
    print(get_data())
