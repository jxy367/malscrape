from __future__ import absolute_import
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .anime_id_list import Idscraper


def run():
    count = 0

    if count == 0:
        process = CrawlerProcess(get_project_settings())
        print("process crawl")
        spider = process.crawl(Idscraper, [0, 1])
        print("start process")
        print(count)
        process.start(True)
        count += 1
        print("Should be plus 1: " + str(count))

