import scrapy
from malscrape.items import *
#from datetime import datetime
import re


class Mangscraper(scrapy.Spider):
    name = "mal_scraper"

    num_pages = 14

    start_urls = []

    for num in range(0,num_pages):
        item_number = num*50
        start_urls.append("https://myanimelist.net/manga.php?q=&type=1&score=0&status=0&mid=0&sm=0&sd=0&sy=0&em=0&ed=0&ey=0&c[0]=b&c[1]=g&c[2]=c&c[3]=d&gx=0&genre[0]=35&show=" + str(item_number) + "")

    def parse(self, response):
        for href in response.xpath("//a[@class='hoverinfo_trigger fw-b']/@href"):
            url = href.extract().strip()
            yield scrapy.Request(url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        item = MangItem()

        item["title"] = response.xpath("//h1/descendant::text()").extract()[0]
        list_authors = response.xpath("//div/span[contains(text(), 'Authors')]/following-sibling::a/text()").extract()
        authors = ""
        first = True
        for author in list_authors:
            if not first:
                authors = authors + "|"
            try:
                author = author.strip()
                last, first = author.split(',')
                last = last.strip()
                first = first.strip()
                author = last+','+first
                authors = authors + author
            except ValueError:
                authors = authors + author
            first = False
        #authors = authors + " ]"


        item["authors"] = authors
        item["num_vol"] = response.xpath("//div/span[contains(text(),'Volumes')]/ancestor::div[contains(@class, 'spaceit')]/text()").extract()[0].strip()
        item["num_chap"] = response.xpath("//div/span[contains(text(),'Chapters')]/parent::*/text()").extract()[0].strip()
        item["status"] = response.xpath("//div/span[contains(text(),'Status')]/ancestor::div[contains(@class, 'spaceit')]/text()").extract()[0].strip()
        try:
            item["mal_score"] = response.xpath("//span[contains(@itemprop, 'ratingValue')]/text()").extract()[0].strip()
        except IndexError:
            item["mal_score"] = "".join(response.xpath("//span[contains(text(), 'Score')]/parent::div[contains(@data-id,'info1')]/text()").extract()).strip()
        try:
            item["mal_ranking"] = "".join(response.xpath("//td[contains(@class, 'borderClass')]//span[contains(text(),'Ranked')]/parent::div[contains(@data-id,'info2')]/text()").extract()).strip().split("#")[1]
        except IndexError:  # N/A Rank
            item["mal_ranking"] = "".join(response.xpath("//td[contains(@class, 'borderClass')]//span[contains(text(),'Ranked')]/parent::div[contains(@data-id,'info2')]/text()").extract()).strip().split("#")[0]
        item["mal_popularity"] = response.xpath("//span[contains(text(),'Popularity')]/parent::*/text()").extract()[0].strip().split("#")[1]
        item["mal_url"] = response.xpath("//meta[@property='og:url']/@content").extract()[0].strip()

        list_of_synopsis = response.xpath("//span[@itemprop='description']/text()").extract()
        synopsis = ""
        for part in list_of_synopsis:
            part = part.strip()
            synopsis = synopsis + " " + part

        item["synopsis"] = synopsis

        item["Action"] = 0
        item["Adventure"]= 0
        item["Cars"]= 0
        item["Comedy"]= 0
        item["Dementia"]= 0
        item["Demons"]= 0
        item["Doujinshi"]= 0
        item["Drama"]= 0
        item["Ecchi"]= 0
        item["Fantasy"]= 0
        item["Game"]= 0
        item["GenderBender"]= 0
        item["Harem"]= 0
        item["Hentai"]= 0
        item["Historical"]= 0
        item["Horror"]= 0
        item["Josei"]= 0
        item["Kids"]= 0
        item["Magic"]= 0
        item["MartialArts"]= 0
        item["Mecha"]= 0
        item["Military"]= 0
        item["Music"]= 0
        item["Mystery"]= 0
        item["Parody"]= 0
        item["Police"]= 0
        item["Psychological"]= 0
        item["Romance"]= 0
        item["Samurai"]= 0
        item["School"]= 0
        item["SciFi"]= 0
        item["Seinen"]= 0
        item["Shoujo"]= 0
        item["ShoujoAi"]= 0
        item["Shounen"]= 0
        item["ShounenAi"]= 0
        item["SliceofLife"]= 0
        item["Space"]= 0
        item["Sports"]= 0
        item["SuperPower"]= 0
        item["Supernatural"]= 0
        item["Thriller"]= 0
        item["Vampire"]= 0
        item["Yaoi"]= 0
        item["Yuri"]= 0

        list_of_genres = response.xpath("//span[text()='Genres:']/following-sibling::*/text()").extract()
        genres = ""
        first = True
        for genre in list_of_genres:
            genre = genre.strip()
            genre = re.sub('[^A-Za-z0-9]+', '', genre)
            item[genre] = 1
            if first:
                genres = genres + genre
                first = False
            else:
                genres = genres + ", " + genre
        item["genres"] = genres

        yield item

class Bakascraper(scrapy.Spider):
    name = "Tsundere_scraper"

    num_pages = 37

    start_urls = []

    for num in range(1,num_pages+1):
        start_urls.append("http://www.mangaupdates.com/series.html?page=" + str(num) + "&perpage=50&type=manga&genre=Harem")

    def parse(self, response):
        for href in response.xpath("//td[@class = 'text pad col1']/a/@href").extract():
            url = href.strip()
            yield scrapy.Request(url, callback=self.parse_dir_content)

    def parse_dir_content(self, response):
        item = BakaItem()

        item["title"] = response.xpath("//span[@class='releasestitle tabletitle']/text()").extract()[0].strip()

        vol_and_status = response.xpath("//div[@class='sCat']/b[text()='Status in Country of Origin']/parent::*/following-sibling::*/text()").extract()[0].strip()
        num_vol = re.search(r'\d+', vol_and_status).group()
        possible_status = ["Ongoing", "Incomplete", "Complete", "Discontinued", "NA", "Unknown"]
        status = ''
        for p_status in possible_status:
            if status == '':
                if p_status in vol_and_status:
                    status = p_status

        if status == '':
            status = "Unknown"

        item["num_vol"] = num_vol
        item["status"] = status
        item["baka_url"] = response.url
        list_synopsis = response.xpath("//div[@class='sCat']/b[text()='Description']/parent::*/following-sibling::*/text()").extract()
        synopsis = ""
        for part in list_synopsis:
            part = part.strip()
            if part == "Manga":
                break
            else:
                synopsis = synopsis + part + " "

        item["synopsis"] = synopsis

        item["Action"] = 0
        item["Adult"] = 0
        item["Adventure"] = 0
        item["Comedy"] = 0
        item["Doujinshi"] = 0
        item["Drama"] = 0
        item["Ecchi"] = 0
        item["Fantasy"] = 0
        item["GenderBender"] = 0
        item["Harem"] = 0
        item["Hentai"] = 0
        item["Historical"] = 0
        item["Horror"] = 0
        item["Josei"] = 0
        item["Lolicon"] = 0
        item["MartialArts"] = 0
        item["Mature"] = 0
        item["Mecha"] = 0
        item["Mystery"] = 0
        item["Psychological"] = 0
        item["Romance"] = 0
        item["SchoolLife"] = 0
        item["Scifi"] = 0
        item["Seinen"] = 0
        item["Shotacon"] = 0
        item["Shoujo"] = 0
        item["ShoujoAi"] = 0
        item["Shounen"] = 0
        item["ShounenAi"] = 0
        item["SliceofLife"] = 0
        item["Smut"] = 0
        item["Sports"] = 0
        item["Supernatural"] = 0
        item["Tragedy"] = 0
        item["Yaoi"] = 0
        item["Yuri"] = 0

        list_genres = response.xpath("//div/b[text()='Genre']/parent::*/following-sibling::*[1]/a[@rel='nofollow']/u/text()").extract()
        genres = ""
        first = True
        for genre in list_genres:
            genre = genre.strip()
            genre = re.sub('[^A-Za-z0-9]+', '', genre)
            item[genre] = 1
            if first:
                genres = genres + genre
                first = False
            else:
                genres = genres + ", " + genre

        item["genres"] = genres
        yield item

#class Harscraper(scrapy.Spider):
#    name = "Har_scraper"

#    num_pages = 2

#    start_urls = []

#    for num in range(1,num_pages+1):
#        start_urls.append("https://myanimelist.net/manga/genre/35/Harem?page="+str(num)+"")

#    def parse(self, response):
  #      for href in response.xpath("//a[contains(@class, 'link-title')]//@href"):
  #          url = href.extract().strip()
  #          yield scrapy.Request(url, callback=self.parse_manga)

 #   def parse_manga(self, response):
 #       for href in response.xpath("//div[contains(@class,'detail-characters-list')]//td[contains(@class, 'borderClass')]/a//@href"):
 #           url = href.extract().strip()
 #           yield scrapy.Request(url, callback = )

  #  def parse_character(self, response):

