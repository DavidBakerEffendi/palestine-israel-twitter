from typing import Set, List
import requests
import datetime as dt


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
            out_dict[dt.datetime(int(raw_dt[0]), int(raw_dt[1]), int(raw_dt[2]))] = url
        elif "apnews" in url:
            pass
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
