from typing import Set, List
import requests
import datetime as dt
from bs4 import BeautifulSoup as bs
import re
import calendar


def read_files(path: str) -> Set[str]:
    try:
        with open(path, 'r') as f:
            return set([str(l).strip() for l in f.readlines()])
    except Exception as _:
        return set([])


def parse_dates(urls: Set[str]):
    out_dict = {}
    for url in urls:
        if "ewn" in url:
            raw_dt = url.strip("https://ewn.co.za/")[:10].split('/')
            date = dt.datetime(int(raw_dt[0]), int(raw_dt[1]), int(raw_dt[2]))
            out_dict[date] = ("EWN", url)
        elif "https://apnews.com/" in url:
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            for match in soup.select('span[data-key="timestamp"]'):
                gs = re.match(r"^(\w+)[ ](\d+)[, ]+(\d+).*$", match.string)
                month_num = list(calendar.month_name).index(gs.group(1))
                day_num = gs.group(2)
                year_num = gs.group(3)
                date = dt.datetime(int(year_num), int(month_num), int(day_num))
                out_dict[date] = ("AP News", url)
        elif "bbc" in url:
            pass
        elif "un.org" in url:
            pass
    return out_dict


def get_data():
    urls = read_files("./resources/media_articles.txt")
    return parse_dates(urls)


if __name__ == "__main__":
    print(get_data())
