import scrapy
from scrapy import Request
from lxml import etree
import time
import re
from ..items import EastmoneyItem


class eastmoneySpider(scrapy.Spider):
    name = 'eastmoney'
    allowed_domains = ['eastmoney.com']

    start_urls = ['https://fund.eastmoney.com/data/fundranking.html']

    def __init__(self, *args, **kwargs):
        super(eastmoneySpider, self).__init__(*args, **kwargs)
        self.start_time = None
        self.request_count = 0
        self.item_count = 0
        self.last_log_time = None
        self.last_request_count = 0
        self.last_item_count = 0

        with open('logs.txt', 'w', encoding='utf-8') as f:
            f.write("Time Elapsed(s) | Total Requests | Total Items | RPS | Items/s\n")
            f.write("----------------------------------------------------------------\n")

    def start_requests(self):
            self.start_time = time.time()
            self.last_log_time = self.start_time
            for i in range(20):
                self.request_count += 1
                url = 'https://fund.eastmoney.com/data/rankhandler.aspx'
                params = {
                    'op': 'ph',
                    'dt': 'kf',
                    'ft': 'all',
                    'rs': '',
                    'gs': '0',
                    'sc': '1nzf',
                    'st': 'desc',
                    'sd': '2024-10-11',
                    'ed': '2025-10-11',
                    'qdii': '',
                    'tabSubtype': ',,,,,',
                    'pi': f'{i+1}',
                    'pn': '50',
                    'dx': '0',
                    'v': '0.46581853097453874'
                }

                headers = {
                    'Referer': 'https://fund.eastmoney.com/data/fundranking.html'
                }

                yield scrapy.FormRequest(
                    url=url,
                    formdata=params,
                    headers=headers,
                    callback=self.parse
                )

    def parse(self, response, **kwargs):
        obj1 = re.compile(r'"(?P<contents>.*?)",', re.S)
        contents = obj1.finditer(response.text)
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        time_since_last_log = current_time - self.last_log_time
        if time_since_last_log >= 1.0:
            current_rps = (self.request_count - self.last_request_count) / time_since_last_log
            current_items_per_sec = (self.item_count - self.last_item_count) / time_since_last_log

            log_message = (f"{elapsed_time:.2f}s | {self.request_count} | {self.item_count} | "
                           f"{current_rps:.2f} | {current_items_per_sec:.2f}\n")

            print(log_message.strip())
            with open('logs.txt', 'a', encoding='utf-8') as f:
                f.write(log_message)

            self.last_log_time = current_time
            self.last_request_count = self.request_count
            self.last_item_count = self.item_count
        for content in contents:
            content2 = content.group('contents')
            parts = content2.split(',')
            item = EastmoneyItem()
            item['fund_code'] = parts[0]
            item['date'] = parts[3]
            item['unit_nav'] = parts[4]
            item['accumulated_nav'] = parts[5]
            item['daily_growth_rate'] = parts[6]
            code=item['fund_code']
            child_url=f'https://fund.eastmoney.com/{code}.html'
            self.item_count += 1
            yield Request(url=child_url,callback=self.parse_detail,cb_kwargs={"item": item})

    def parse_detail(self, response, **kwargs):
        item = kwargs['item']
        child_html=etree.HTML(response.text)
        subscribe_status = child_html.xpath('//*[@id="body"]/div[11]/div/div/div[2]/div[2]/div[2]/div[2]/div[1]/span[2]')[0]
        redeem_status = child_html.xpath('//*[@id="body"]/div[11]/div/div/div[2]/div[2]/div[2]/div[2]/div[1]/span[3]')[0]
        item['subscribe_status'] = subscribe_status.text
        item['redeem_status'] = redeem_status.text
        return item

    def closed(self, reason):
        total_time = time.time() - self.start_time
        avg_rps = self.request_count / total_time
        avg_items_per_sec = self.item_count / total_time

        final_log = (f"\nFinal Statistics:\n"
                     f"Total time: {total_time:.2f}s\n"
                     f"Total requests: {self.request_count}\n"
                     f"Total items: {self.item_count}\n"
                     f"Average RPS: {avg_rps:.2f}\n"
                     f"Average Items/s: {avg_items_per_sec:.2f}\n")

        print(final_log)
        with open('logs.txt', 'a', encoding='utf-8') as f:
            f.write(final_log)