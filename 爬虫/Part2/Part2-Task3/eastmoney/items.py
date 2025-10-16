# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class EastmoneyItem(scrapy.Item):
    fund_code = scrapy.Field()
    date = scrapy.Field()
    unit_nav = scrapy.Field()
    accumulated_nav = scrapy.Field()
    daily_growth_rate = scrapy.Field()
    subscribe_status=scrapy.Field()
    redeem_status=scrapy.Field()
