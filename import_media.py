from typing import Set, List, Dict
import requests
import datetime as dt
from bs4 import BeautifulSoup as bs
import re
import calendar

from selenium.common.exceptions import TimeoutException

import config as conf
import pickle as pk
import os.path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait

import expert_ai_api


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


def configure_firefox_driver():
    # Add additional Options to the webdriver
    firefox_options = FirefoxOptions()
    # add the argument and make the browser Headless.
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    return driver


def scrape_media_text(url: str) -> str:
    blacklist = [
        'style',
        'script',
        'header'
    ]
    out = ""
    if "https://apnews.com/" in url:
        driver = configure_firefox_driver()
        try:
            driver.get(url)
            WebDriverWait(driver, 180).until(
                lambda h: h.find_element_by_class_name('Article').is_displayed()
            )
            ps = driver.find_elements_by_tag_name('p')
            for p in ps:
                out += " {}".format(p.text)
        finally:
            driver.close()
    else:
        page = requests.get(url)
        html = page.text
        soup = bs(html, 'html5lib')
        if "https://www.bbc.com" in url:
            blacklist.append("span")
        elements = [t for t in soup.find_all('p') if t.parent.name not in blacklist]
        for i, s in enumerate(elements):
            out += " {}".format(s.getText())
    return out


def parse_dates(urls: Set[str]) -> Dict[dt.datetime, Dict[str, List[str]]]:
    out_dict = {}
    for url in urls:
        print("Scraping " + url)
        if "https://ewn.co.za/" in url:
            raw_dt = url.strip("https://ewn.co.za/")[:10].split('/')
            date = dt.datetime(int(raw_dt[0]), int(raw_dt[1]), int(raw_dt[2]))
            insert_new_url(out_dict, date, "EWN", url)
        elif "https://apnews.com/" in url:
            driver = configure_firefox_driver()
            try:
                driver.get(url)
                WebDriverWait(driver, 60).until(
                    lambda h: h.find_element_by_class_name('CardHeadline').is_displayed()
                )
                p = driver.find_element_by_css_selector('span[data-key="timestamp"]')
                gs = re.match(r"^(\w+)[ ](\d+)[, ]+(\d+).*$", p.text)
                month_num = list(calendar.month_name).index(gs.group(1))
                day_num = gs.group(2)
                year_num = gs.group(3)
                date = dt.datetime(int(year_num), int(month_num), int(day_num))
                insert_new_url(out_dict, date, "Associated Press", url)
            finally:
                driver.close()
        elif "https://www.bbc.com/" in url:
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            match = soup.select('time[data-testid="timestamp"]')[0]
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


def serialize(path: str, obj: any):
    with open(path, "wb") as mu:
        pk.dump(obj, mu)


def deserialize(path: str) -> any:
    with open(path, "rb") as mu:
        return pk.load(mu)


def get_data() -> Dict[dt.datetime, Dict[str, List[str]]]:
    """
    Reads the URLs from "./resources/media_articles.txt" and organizes these by date and news outlet.
    :return a dictionary with keys being datetime and values being strings to lists of URLs.
    """
    mu_pickle = "./media_urls.pickle"
    print("Getting media objects... ", end="")
    if os.path.isfile(mu_pickle):
        out_dict = deserialize(mu_pickle)
    else:
        urls = read_files(conf.MEDIA_URLS_PATH)
        out_dict = parse_dates(urls)
        serialize(mu_pickle, out_dict)
    print("Success!")
    return out_dict


def get_scraped_text(media_data: Dict[dt.datetime, Dict[str, List[str]]]) -> Dict[dt.datetime, Dict[str, List[str]]]:
    scraped_data = {}
    for (date, media_map) in media_data.items():
        data_per_media_outlet = {}
        for (media_outlet, urls) in media_map.items():
            data_per_media_outlet[media_outlet] = []
            for u in urls:
                try:
                    text = scrape_media_text(u)
                    if len(text) < 5:
                        print("Unsuccessful scrape {}".format(u))
                    else:
                        data_per_media_outlet[media_outlet].append(text)
                except TimeoutException:
                    print("Unsuccessful scrape {} (timeout)".format(u))
        scraped_data[date] = data_per_media_outlet
    return scraped_data


def scraped_data(media_data: Dict[dt.datetime, Dict[str, List[str]]]) -> Dict[dt.datetime, Dict[str, List[str]]]:
    mu_pickle = "./scraped_data.pickle"
    print("Scraping media objects... ", end="")
    if os.path.isfile(mu_pickle):
        scraped_data = deserialize(mu_pickle)
    else:
        scraped_data = get_scraped_text(media_data)
        serialize(mu_pickle, scraped_data)
    print("Success!")
    return scraped_data


if __name__ == "__main__":
    media_data = get_data()
    scraped_data = scraped_data(media_data)
    print(scraped_data)
    # expert_ai_api.publish_credentials()
    # expert_ai_api.obtain_keyphrases(text, 'en')
