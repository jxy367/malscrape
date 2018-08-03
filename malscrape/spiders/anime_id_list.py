import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
import re
from sys import exit


class Idscraper(scrapy.Spider):
    name = "anime_id_scraper"
    start_urls = []

    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse_item"
        )
    ]

    custom_settings = {
        'BOT_NAME': 'malscrape',
        'SPIDER_MODULES': ['malscrape.spiders'],
        'NEWSPIDER_MODULE': 'malscrape.spiders',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZED_DOWNLOAD_DELAY': True,
        'DOWNLOADER_MIDDLEWARES': {
            'malscrape.middlewares.MalscrapeRetryMiddleware': 90,
            'scrapy_proxies.RandomProxy': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'malscrape.middlewares.RotateUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {'malscrape.pipelines.UrlMembersPipeline': 300},
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.2,
        #'CONCURRENT_REQUESTS_PER_IP': 1,
        'LOG_LEVEL': 'INFO',
        'PROXY_MODE': 0,
        'PROXY_LIST': 'list.txt',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }

    def __init__(self, nums=[], *args, **kwargs):
        super(Idscraper, self).__init__(*args, **kwargs)
        logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        logger.setLevel(logging.INFO)
        self.start_num = nums[0]
        self.end_num = nums[1]

    def start_requests(self):
        requests = []
        for num in range(int(self.start_num), int(self.end_num)):
            requests.append(scrapy.Request("https://myanimelist.net/topanime.php?limit=" + str(50*num)))
        return requests

    def parse(self, response):
        if not response.xpath("//a[@class='link-mal-logo']/text()").extract()[0] == 'MyAnimeList.net':
            yield scrapy.Request(url=response.url, dont_filter=True)
        else:
            #print(re.findall('\d+', response.url)[0])
            anime_ids = []
            anime_urls = []
            for href in response.xpath("//a[@class='hoverinfo_trigger fl-l ml12 mr8']/@href").extract():
                url = href.strip()
                #print(url)
                anime_urls.append(url)
                anime_id = re.findall('\d+', url)[0]
                anime_ids.append(anime_id)

            assert len(anime_ids) == len(anime_urls)

            num_members_list = []
            for href in response.xpath("//div[@class='information di-ib mt4']/text()").extract():
                if 'members' in href:
                    num_members = "".join(re.findall('\d+', href))
                    num_members_list.append(num_members)

            assert len(anime_ids) == len(num_members_list)

            for anime_id in anime_ids:
                item = dict()
                item['anime_id'] = anime_id
                item['num_members'] = num_members_list[anime_ids.index(anime_id)]
                item['url'] = anime_urls[anime_ids.index(anime_id)].encode('utf-8')
                yield item


    def get_num_members(self, response):
        item = response.meta['item']
        string_num_members = response.xpath("//span[@class='dark_text'][text()='Members:']/parent::div/text()").extract()[1]
        num_members = "".join(re.findall('\d+', string_num_members))
        item['num_members'] = num_members
        #print("yielding")
        yield item


# Anime or Manga spider
class Malscraper(scrapy.Spider):
    name = "mal_scraper"
    start_urls = []

    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse_item"
        )
    ]

    custom_settings = {
        'BOT_NAME': 'malscrape',
        'SPIDER_MODULES': ['malscrape.spiders'],
        'NEWSPIDER_MODULE': 'malscrape.spiders',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZED_DOWNLOAD_DELAY': True,
        'DOWNLOADER_MIDDLEWARES': {
            'malscrape.middlewares.MalscrapeRetryMiddleware': 90,
            'scrapy_proxies.RandomProxy': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'malscrape.middlewares.RotateUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {'malscrape.pipelines.UrlMembersPipeline': 300},
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.2,
        #'CONCURRENT_REQUESTS_PER_IP': 1,
        'LOG_LEVEL': 'INFO',
        'PROXY_MODE': 0,
        'PROXY_LIST': 'list.txt',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }

    def __init__(self, nums=[], *args, **kwargs):
        super(Malscraper, self).__init__(*args, **kwargs)
        logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        logger.setLevel(logging.INFO)
        self.start_num = nums[0]
        self.end_num = nums[1]
        self.anime_or_manga = nums[2]

    def start_requests(self):
        requests = []
        for num in range(int(self.start_num), int(self.end_num)):
            requests.append(scrapy.Request("https://myanimelist.net/top" + self.anime_or_manga + ".php?limit=" + str(50*num)))
        return requests

    def parse(self, response):
        if not response.xpath("//a[@class='link-mal-logo']/text()").extract()[0] == 'MyAnimeList.net':
            yield scrapy.Request(url=response.url, dont_filter=True)
        else:
            #print(re.findall('\d+', response.url)[0])
            urls = []
            for href in response.xpath("//a[@class='hoverinfo_trigger fl-l ml12 mr8']/@href").extract():
                url = href.strip()
                urls.append(url)

            num_members_list = []
            for href in response.xpath("//div[@class='information di-ib mt4']/text()").extract():
                if 'members' in href:
                    num_members = "".join(re.findall('\d+', href))
                    num_members_list.append(num_members)

            assert len(urls) == len(num_members_list)

            for url in urls:
                item = dict()
                item['num_members'] = num_members_list[urls.index(url)]
                item['url'] = urls[urls.index(url)].encode('utf-8')
                yield item

    def get_num_members(self, response):
        item = response.meta['item']
        string_num_members = response.xpath("//span[@class='dark_text'][text()='Members:']/parent::div/text()").extract()[1]
        num_members = "".join(re.findall('\d+', string_num_members))
        item['num_members'] = num_members
        #print("yielding")
        yield item


# Spider for scraping users from url_member list
class UserScraper(scrapy.Spider):
    name = "username_scraper"

    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse_item"
        )
    ]

    custom_settings = {
        'BOT_NAME': 'malscrape',
        'SPIDER_MODULES': ['malscrape.spiders'],
        'NEWSPIDER_MODULE': 'malscrape.spiders',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZED_DOWNLOAD_DELAY': True,
        'DOWNLOADER_MIDDLEWARES': {
            'malscrape.middlewares.MalscrapeRetryMiddleware': 90,
            'scrapy_proxies.RandomProxy': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'malscrape.middlewares.RotateUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {'malscrape.pipelines.UsernameListPipeline': 300},
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 50,
        'LOG_LEVEL': 'WARNING',
        'PROXY_MODE': 0,
        'PROXY_LIST': 'list.txt',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
    }

    def __init__(self, anime_dict=dict, *args, **kwargs):
        super(UserScraper, self).__init__(*args, **kwargs)
        #logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        #logger.setLevel(logging.INFO)
        assert type(anime_dict) is dict
        self.anime_dict = anime_dict

    def start_requests(self):
        members_per_page = 75
        requests = []
        for anime_url in self.anime_dict.keys():
            num_members = int(self.anime_dict[anime_url])
            member_count = num_members
            if num_members > 7500:
                member_count = 7500
            base_url = anime_url + "/stats?m=all&show="
            for num in range(0, member_count, members_per_page):
                if num == 7500:
                    requests.append(scrapy.Request(base_url+str(7499)))
                else:
                    requests.append(scrapy.Request(base_url+str(num)))
        #print(requests)
        return requests

    def parse(self, response):
        if not response.xpath("//a[@class='link-mal-logo']/text()").extract()[0] == 'MyAnimeList.net':
            yield scrapy.Request(url=response.url, dont_filter=True)
        else:
            item = {}
            username_list = []
            usernames = response.xpath("//div[@class='di-tc va-m al pl4']/child::a/text()").extract()
            for username in usernames:
                username = username.strip()
                username_list.append(username)

        #print(username_list)
            item['usernames'] = username_list
            yield item


def mal_members_scraper(num_pages: int, num_spiders: int, anime_or_manga: str):
    anime_max_pages = 300
    manga_max_pages = 950

    # Value checks
    try:
        if anime_or_manga != "anime" and anime_or_manga != "manga":
            raise ValueError('anime_or_manga argument was not "anime" or "manga". Instead was "' + anime_or_manga + '"')

        if num_spiders < 1:
            raise ValueError('num_spiders must be 1 or more. Instead was ' + str(num_spiders))
        num_spiders = num_spiders // 1

        if num_pages < 1:
            print("num_pages was less than 1. Searching all pages")
            if anime_or_manga == "anime":
                num_pages = anime_max_pages

            elif anime_or_manga == "manga":
                num_pages = manga_max_pages

            else:
                raise ValueError('anime_or_manga was not "anime" or "manga". This should never happen.')
        num_pages = num_pages // 1

    except ValueError:
        raise

    # Reset "url_members.txt" for this run
    reset_file("url_members.txt")

    args_list = []

    # Split number of pages among the number of spiders and creating arguments for each
    for sp in range(0, num_spiders):
        start_num = sp*num_pages//num_spiders
        end_num = (sp + 1)*num_pages//num_spiders
        if sp == num_spiders:
            end_num = num_pages
        args_list.append((start_num, end_num, anime_or_manga))

    # Start each spider with their arguments
    start_malscrapers(args_list)


def start_malscrapers(args_list):
    # Value checks
    try:
        if len(args_list) < 1:
            raise ValueError("args_list length less than 1. THIS SHOULD NEVER HAPPEN")

    except ValueError:
        raise

    # Process that holds spiders
    process = CrawlerProcess()
    for args in args_list:
        # Add spiders and arguments to each spider
        arguments = list(args)
        process.crawl(process.create_crawler(Malscraper), arguments)
    process.start(True)


def anime_url_members_scrape(num_pages, num_spiders):
    reset_file("url_members.txt")
    start_ends = []
    for sp in range(0, num_spiders):
        start_num = sp*num_pages//num_spiders
        end_num = (sp + 1)*num_pages//num_spiders
        if sp == num_spiders:
            end_num = num_pages
        start_ends.append((start_num, end_num))

    start_idscrapers(start_ends)


def start_idscrapers(start_ends):
    process = CrawlerProcess()
    for values in start_ends:
        arguments = list(values)
        process.crawl(process.create_crawler(Idscraper), arguments)
    process.start(True)


def load_byte_dict(filename):
    new_dict = dict()
    dict_file = open(filename, 'r')
    for line in dict_file:
        line = line.strip()
        line = line[2:]
        values = line.rsplit(":", 1)
        assert values[0] not in new_dict.keys(), str(values[0]) + ":" + str(new_dict.keys())
        new_dict[values[0]] = values[1]

    return new_dict


def balance(data_dict, num_dicts):
    current_values = []
    num_pages_values = []
    list_dicts = []
    for num in range(0, num_dicts):
        list_dicts.append(dict())
        current_values.append(0)
        num_pages_values.append(0)

    for key in data_dict.keys():
        value = data_dict[key]
        int_value = int(value)
        assert int_value >= 0
        item_weight = int_value if int_value < 7500 else 7500
        min_index = num_pages_values.index(min(num_pages_values))
        current_values[min_index] = current_values[min_index] + item_weight
        num_pages_values[min_index] = num_pages_values[min_index] + item_weight//75
        if item_weight % 75 != 0:
            num_pages_values[min_index] = num_pages_values[min_index] + 1
        list_dicts[min_index][key] = value

    len_dicts = []
    for dictionary in list_dicts:
        len_dicts.append(len(dictionary.keys()))

    print(sorted(current_values))
    print("weight range: " + str(max(current_values) - min(current_values)))

    print(sorted(num_pages_values))
    print("num pages range: " + str(max(num_pages_values) - min(num_pages_values)))

    print(sorted(len_dicts))
    print("length range: " + str(max(len_dicts) - min(len_dicts)))

    return list_dicts


def user_scrape(filename, num_spiders):
    id_members_dict = load_byte_dict(filename)
    list_dicts = balance(id_members_dict, num_spiders)
    start_userscrapers(list_dicts)


def start_userscrapers(list_dicts):
    reset_file("user_gathering_data.txt")
    reset_file("usernames.txt")
    process = CrawlerProcess()
    for dictionary in list_dicts:
        argument = dictionary
        process.crawl(process.create_crawler(UserScraper), argument)
    process.start(True)


def reset_file(filename):
    f = open(filename, 'w')
    f.close()


def consolidate_usernames(filename):
    username_list = set()
    file = open(filename, 'r')
    count = 0
    for line in file:
        line = line.strip()
        username_list.add(line)
        count = count + 1
        if count % 10000 == 0:
            print("Count: " + str(count) + ", Number of Usernames: " + str(len(username_list)))

    file.close()

    print("Number of Usernames: " + str(len(username_list)))

    file = open(filename, 'w')

    for username in username_list:
        file.write(username + "\n")

    file.close()

#mal_members_scraper(-1, 3, "manga")
user_scrape("all_manga_url_members.txt", 50)
#consolidate_usernames("usernames.txt")