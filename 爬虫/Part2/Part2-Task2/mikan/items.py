# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MikanItem(scrapy.Item):
    size=scrapy.Field()
    size_bytes=scrapy.Field()
    name=scrapy.Field()
    torrent=scrapy.Field()
    trans=scrapy.Field()
    file_format=scrapy.Field()
    season=scrapy.Field()
    encode=scrapy.Field()
    resolution=scrapy.Field()
    language=scrapy.Field()
    episode=scrapy.Field()
    title=scrapy.Field()
    time=scrapy.Field()