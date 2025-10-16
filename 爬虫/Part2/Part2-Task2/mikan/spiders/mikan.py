import time
import scrapy
from scrapy.http import HtmlResponse
from scrapy import Request
from lxml import etree
from mikan.items import MikanItem
import re


def convert_to_bytes(size_str):
    size_str = size_str.upper().strip()
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    import re
    match = re.match(r'([\d.]+)\s*([A-Z]+)', size_str)
    if not match:
        raise ValueError(f"无法解析大小字符串: {size_str}")
    number = float(match.group(1))
    unit = match.group(2)
    if unit not in units:
        raise ValueError(f"不支持的单位: {unit}")
    return int(number * units[unit])

class MikanSpider(scrapy.Spider):
    name = "mikan"
    allowed_domains = ["mikan.tangbai.cc"]
    start_urls = ["https://mikan.tangbai.cc/Home/Classic"]

    def __init__(self, *args, **kwargs):
        super(MikanSpider, self).__init__(*args, **kwargs)
        self.start_time = None
        self.request_count = 0
        self.item_count = 0
        self.last_log_time = None
        self.last_request_count = 0
        self.last_item_count = 0

        with open('logs.txt', 'w', encoding='utf-8') as f:
            f.write("Time Elapsed(s) | Total Requests | Total Items | RPS | Items/s\n")
            f.write("------------------------------------------------------scrapy ----------\n")

    def start_requests(self):
        self.start_time = time.time()
        self.last_log_time = self.start_time
        for classic in range(100):
            self.request_count += 1
            print(f"https://mikan.tangbai.cc/Home/Classic/{classic+1}")
            yield Request(url=f"https://mikan.tangbai.cc/Home/Classic/{classic+1}")

    def parse(self, response: HtmlResponse, **kwargs):
        response_html = etree.HTML(response.text)
        contents = response_html.xpath('//*[@id="sk-body"]/table/tbody/tr')
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
            movie_item = MikanItem()
            movie_item['time'] = content.xpath('./td[1]/text()')[0]
            movie_item['size'] = content.xpath('./td[4]/text()')[0]
            size=content.xpath('./td[4]/text()')[0]
            size_bytes = convert_to_bytes(size)
            print(f"{size}={size_bytes}bytes")
            movie_item['size_bytes'] = size_bytes
            movie_item['name'] = content.xpath('./td[3]/a[1]/text()')[0]
            movie_item['torrent'] = content.xpath('./td[3]/a/@href')
            file=content.xpath('./td[3]/a[1]/text()')[0]
            print(file)
            movie_item['trans'] = content.xpath('./td[2]/a/text()')
            file_format_obj = [r'mp4', r'MP4', r'MKV']
            pattern1 = r"|".join(map(re.escape, file_format_obj))
            movie_item['file_format'] = re.findall(pattern1, file)
            season_obj = [
                r'(?:Season\s*)(\d+)',
                r'(?:S(\d+))(?:\s|$)',
                r'(?:第\s*)(\d+)(?:\s*季)',
                r'(?:\s*(\d+)(?:nd|rd|th)?\s*Season)',
            ]
            pattern2 = r"|".join(season_obj)
            seasons = re.findall(pattern2, file, re.IGNORECASE)
            if seasons:
                for match in seasons:
                    seasons_num = [group for group in match if group]
                    if seasons_num:
                        movie_item['season'] = seasons_num[0]
                        break
            encode_obj = [r'(HEVC|H\.265)', r'(AVC|H\.264|x264)',
                          r'(AAC|AC3|FLAC|MP3)',
                          r'(10-?bit|8-?bit)',
                          r'(WEB-?DL|WebRip|BDRip|BDRemux)',
                          r'(HEVC-10bit)',
                          r'(AVC 8bit AAC)'
                          ]
            pattern3 = r"|".join(encode_obj)
            encodes = re.findall(pattern3, file, re.IGNORECASE)
            if encodes:
                for match in encodes:
                    encode_nums = [group for group in match if group]
                    if encode_nums:
                        movie_item['encode'] = encode_nums[0]
                        # print(encode)
                        break
            resolution_obj = [r'(\d{3,4}[Pp])',
                              r'(\d+x\d+)',
                              r'(4K|1080P|720P|480P)',
                              ]
            pattern4 = r"|".join(resolution_obj)
            resolutions = re.findall(pattern4, file, re.IGNORECASE)
            if resolutions:
                for match in resolutions:
                    resolution_nums = [group for group in match if group]
                    if resolution_nums:
                        movie_item['resolution'] = resolution_nums[0]
                        # print(resolution)
                        break
            language_obj = [r'(简体|简日|简内)',
                            r'(繁体|繁日|繁内)',
                            r'(中文|CH[ST]|GB|BIG5)',
                            r'(日语|日文|JP)',
                            r'(英语|英文|EN)',
                            r'(双语|双語)',
                            r'(内封|内嵌)',
                            ]
            pattern5 = r"|".join(language_obj)
            languages = re.findall(pattern5, file)
            if languages:
                for match in languages:
                    language_nums = [group for group in match if group]
                    if language_nums:
                        movie_item['language'] = language_nums[0]
                        # print(language)
                        break
            episode_obj = [r'(?:-\s*)(\d+)(?:\s|\[|\(|$)',
                           r'(?:【)(\d+)(?:】)',
                           r'(?:\[)(\d+)(?:\])',
                           r'(?:EP?)(\d+)',
                           r'(?:第\s*)(\d+)(?:\s*集)',
                           r'(?:\s)(\d+)(?:\s*(?:\[|\]|【|】|\(|\)|$))',
                           ]
            pattern6 = r"|".join(episode_obj)
            episodes = re.findall(pattern6, file)
            if episodes:
                for match in episodes:
                    episodes_nums = [group for group in match if group]
                    if episodes_nums:
                        movie_item['episode'] = episodes_nums[0]
                        break
            title_obj = [r'^【.*?】.*?【.*?】.*?【([^】]+?)】',
                         r'(?:^\[.*?\]|^【.*?】)\s*([^【\[\]\n-]+?)(?:\s*-\s*\d+)',
                         r'(?:^\[.*?\]|^【.*?】)\s*([^\/\n]+?)(?:\s*\/[^\/]*)?(?:\s*-\s*\d+)',
                         r'^([^\/\n]+?)(?:\s*\/[^\/]*)?(?:\s*-\s*\d+)',
                         r'(?:^\[.*?\]|^【.*?】)\s*([^【\[\]\n]+?)(?=\s*\[|\s*【|$)',
                         r'(?:^\[.*?\]|^【.*?】)\s*([^【\[\]\n]+?)(?=\s*【\d+】|$)',
                         ]
            pattern7 = r"|".join(title_obj)
            titles = re.findall(pattern7, file)
            if titles:
                for match in titles:
                    titles_nums = [group for group in match if group]
                    if titles_nums:
                        movie_item['title'] = titles_nums[0]
                        break
            self.item_count += 1
            yield movie_item

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

