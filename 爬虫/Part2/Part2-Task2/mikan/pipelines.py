# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pymysql


class MikanPipeline:
    def __init__(self):
        self.conn = pymysql.connect(host='yichendeMacBook-Pro.local',port=3306,
                                    user='root',passwd='dxst131499',db='mikan',charset='utf8mb4')
        self.cursor = self.conn.cursor()


    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
            name = item.get('name', '')
            trans = item.get('trans', '')
            title = item.get('title', '')
            season = item.get('season', '0')
            episode = item.get('episode', '0')
            resolution = item.get('resolution', '')
            encode = item.get('encode', '')
            language = item.get('language', '')
            file_format = item.get('file_format', '')
            size_bytes = item.get('size_bytes', '0')
            torrent = item.get('torrent', '')
            times = item.get('time', '')

            import hashlib
            import time
            hash_input = f"{name}{time.time()}"
            file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:16]

            self.cursor.execute(
                'INSERT INTO torrent_files(original_filename, file_size_bytes, fansub_group, anime_title, '
                'season_number, episode_number, resolution, encode_info, language, file_format, torrent_data, file_hash,last_access) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (name, size_bytes, trans, title, season, episode, resolution, encode, language, file_format, torrent,
                 file_hash,times)
            )
            return item