from typing import Set, List, Dict, Tuple
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


def parse_dates(urls: Set[str]) -> Dict[dt, List[Tuple[str, str]]]:
    out_dict = {}
    for url in urls:
        if "https://ewn.co.za/" in url:
            raw_dt = url.strip("https://ewn.co.za/")[:10].split('/')
            date = dt.datetime(int(raw_dt[0]), int(raw_dt[1]), int(raw_dt[2]))
            if date not in out_dict.keys():
                out_dict[date] = [("EWN", url)]
            else:
                out_dict[date].append(("EWN", url))
        elif "https://apnews.com/" in url:
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            for match in soup.select('span[data-key="timestamp"]'):
                gs = re.match(r"^(\w+)[ ](\d+)[, ]+(\d+).*$", match.string)
                month_num = list(calendar.month_name).index(gs.group(1))
                day_num = gs.group(2)
                year_num = gs.group(3)
                date = dt.datetime(int(year_num), int(month_num), int(day_num))
                if date not in out_dict.keys():
                    out_dict[date] = [("Associated Press", url)]
                else:
                    out_dict[date].append(("Associated Press", url))
        elif "https://www.bbc.com/" in url:
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            for match in soup.select('time[data-testid="timestamp"]'):
                gs = re.match(r"^.*datetime=\"(\d+)-(\d+)-(\d+)T.*$", str(match))
                day_num = gs.group(3)
                month_num = gs.group(2)
                year_num = gs.group(1)
                date = dt.datetime(int(year_num), int(month_num), int(day_num))
                if date not in out_dict.keys():
                    out_dict[date] = [("BBC", url)]
                else:
                    out_dict[date].append(("BBC", url))
        elif "https://www.theguardian.com/" in url:
            gs = re.match(r"^https://www.theguardian.com/[\w\-\/]*/(\d+)/(\w+)/(\d+)/.*$", url)
            day_num = gs.group(3)
            month_num = list(calendar.month_name).index(str(gs.group(2)).title())
            year_num = gs.group(1)
            date = dt.datetime(int(year_num), int(month_num), int(day_num))
            if date not in out_dict.keys():
                out_dict[date] = [("The Guardian", url)]
            else:
                out_dict[date].append(("The Guardian", url))
    return out_dict


def get_data() -> Dict[dt, List[Tuple[str, str]]]:
    """
    Reads the URLs from "./resources/media_articles.txt" and organizes these by date and news outlet.
    :return a dictionary with keys being datetime and values being strings to lists of URLs.
    """
    # TODO: Convert to Dict[dt, Dict[str,str]]
    urls = read_files("./resources/media_articles.txt")
    return parse_dates(urls)


if __name__ == "__main__":
    print(get_data())
