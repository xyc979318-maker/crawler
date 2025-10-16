# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from cytoolz.itertoolz import accumulate
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymysql

class EastmoneyPipeline:
    def __init__(self):
        self.conn = pymysql.connect(host='yichendeMacBook-Pro.local', port=3306,
                                    user='root', passwd='dxst131499', db='mydatabase', charset='utf8mb4')
        self.cursor = self.conn.cursor()

    def close_spider(self,spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        fund_code=item.get('fund_code','')
        date=item.get('date','')
        unit_nav=item.get('unit_nav','')
        accumulated_nav=item.get('accumulated_nav','')
        daily_growth_rate=item.get('daily_growth_rate','')
        subscribe_status=item.get('subscribe_status','')
        redeem_status=item.get('redeem_status','')

        self.cursor.execute(
            'INSERT INTO fund_nav(fund_code,date,unit_nav,accumulated_nav,'
            'daily_return,subscribe_status,redeem_status)VALUES(%s,%s,%s,%s,%s,%s,%s)',
            (fund_code,date,unit_nav,accumulated_nav,daily_growth_rate,subscribe_status,redeem_status)
        )
        return item
