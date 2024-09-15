import os

import postprocessing

SCRAPERS = ['joker2019_scraper', 'jpoint2019_scraper', 'jpoint2018_scraper', 'joker2018_scraper']


def run_scrapers():
    for scraper in SCRAPERS:
        os.system(f'scrapy crawl {scraper}  -o output/{scraper}.json')

    postprocessing.run_postrpoc()

run_scrapers()