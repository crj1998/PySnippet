# -*- coding: utf-8 -*-
# @Author: Chen Renjie
# @Date:   2022-08-02 23:41:31
# @Last Modified by:   Chen Renjie
# @Last Modified time: 2022-08-21 15:43:49
 
"""Python for HTTP Live Streaming (HLS)
Reference: https://datatracker.ietf.org/doc/html/draft-pantos-http-live-streaming-23
https://zhuanlan.zhihu.com/p/184577862

https://www.kan.cc/play/753-0-0.html
https://www.ichunqiu.com/course/298
https://sample-videos.com/index.php
 
"""
 
"""
CR  : Carriage Return. 对应ASCII中转义字符\r，表示回车
LF  : Line Feed. 对应ASCII中转义字符\n，表示换行
CRLF: Carriage Return & Line feed. \r\n，表示回车并换行
 
#EXTINF:<DURATION>,<TITLE> 
Durations MUST be integers if the protocol version of the Playlist file is less than 3.

#EXT-X-VERSION:<int>    版本号
#EXT-X-TARGETDURATION:<int>    TS文件的最大持续时间(duration)。只能出现一次
#EXT-X-MEDIA-SEQUENCE:<int>    指明播放列表文件中的第一个URI的序列号。最多出现一次，不出现则为0
#EXT-X-PLAYLIST-TYPE:<EVENT|VOD>    关于Playlist的可变性的信息
#EXT-X-KEY: METHOD=<method> [,URI=<uri>][,IV=<iv>]
#EXT-X-ALLOW-CACHE:<YES|NO>    指定客户端是否准许缓存下载的媒体文件用来重播。它可能会出现在播放列表文件的任何地方，最多出现一次。
#EXT-X-STREAM-INF:[attribute=value][,attribute=value]*<URI>    表示在播放列表中的下一个URI标识另一个播放列表文件。
#EXT-X-DISCONTINUITY
"""

# pip install pycryptodome

import os
import time
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from multiprocessing.pool import ThreadPool
from Crypto.Cipher import AES
 

NUM_THREADS = 1

class HLS:
    HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
    def __init__(self, url: str, headers=None):
        self.url = url
        self.metadata = {
            "EXT-X-VERSION": 3,
            "EXT-X-TARGETDURATION": None,
            "EXT-X-MEDIA-SEQUENCE": 0,
            "EXT-X-PLAYLIST-TYPE": "VOD",
            "EXT-X-KEY": {"METHOD": None, "URI": None, "IV": None},
            "EXT-X-ALLOW-CACHE": False
        }
        self.ts = []
 
        self.parse(url)
     
    @staticmethod
    def istag(s: str):
        return s.strip().startswith("#EXT")
 
    @classmethod
    def decrypt(cipher, key: str, iv):
        aes128 = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        plain = aes128.decrypt(cipher)
        return plain
 
    def parse(self, url: str):
        if os.path.exists(url):
            with open(url, "r") as f:
                text = f.read().strip()
        else:
            r = requests.get(url, timeout=5)
            text = r.text.strip()
        assert text.startswith("#EXTM3U") and text.endswith("#EXT-X-ENDLIST")
        lines = text.split()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if self.istag(line):
                if ":" in line:
                    tag, *data = line.split(":")
                    data = ':'.join(data)
                else:
                    tag = line
                if tag.startswith("#EXTINF"):
                    duration, title = data.split(",")
                    duration = float(duration.strip())
                    i += 1
                    uri = lines[i].strip()
                    self.ts.append((uri, duration))
                elif tag.startswith("#EXT-X-KEY"):
                    for item in data.split(","):
                        key, value = item.split("=")
                        self.metadata["EXT-X-KEY"][key.strip()] = value.strip()
                    uri = self.metadata["EXT-X-KEY"]["URI"].strip('"')
                    uri = self.absolutepath(uri)
                    self.key = requests.get(uri, timeout=5).content
            else:
                pass
 
            i += 1
 
        self.total = round(sum([ts[1] for ts in self.ts])/60, 2)
 
    def absolutepath(self, uri: str):
        if uri.startswith("http"):
            return uri
        elif uri.startswith("/"):
            i = urlparse(self.url)
            return f"{i.scheme}://{i.netloc}{uri}"
        else:
            return f"{os.path.dirname(self.url)}/{uri}"
 
    def download_multi_thread(self, filename):
        cryptor = AES.new(self.key, AES.MODE_CBC, self.key)
 
        urls = [self.absolutepath(ts[0]) for ts in self.ts]
        results = ThreadPool(NUM_THREADS).imap(lambda url: requests.get(url, headers=self.HEADERS, timeout=15).content, urls)
 
        with open(filename, "wb+") as f, tqdm(enumerate(results), unit='B', unit_scale=True) as t:
            for i, content in enumerate(results, start=1):
                if cryptor is not None:
                    content = cryptor.decrypt(content)
                f.write(content)
                f.flush()
                t.update(len(content))
                t.set_postfix({"progress": f"{i/len(urls):.2%}"})
                # print(f"chunk {i+1} done!")
    
    def download(self, filename):
        cryptor = AES.new(self.key, AES.MODE_CBC, self.key)
        # urls = [self.absolutepath(ts[0]) for ts in self.ts]
        url = self.absolutepath(self.ts[0][0])
        url = url.strip("index0.ts")
        index = 0
        with open(filename, "wb+") as f:
            while True:
                try:
                    content = requests.get(url+f"index{index}.ts", headers=self.HEADERS, timeout=15).content
                except:
                    break
                if cryptor is not None:
                    content = cryptor.decrypt(content)
                f.write(content)
                f.flush()
                print(url+f"index{index}.ts")
                index += 1
                time.sleep(0.5)


def download_m3u8(m3u8, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
    }
    metadata = {
        "EXT-X-VERSION": 3,
        "EXT-X-TARGETDURATION": None,
        "EXT-X-MEDIA-SEQUENCE": 0,
        "EXT-X-PLAYLIST-TYPE": "VOD",
        "EXT-X-KEY": {"METHOD": None, "URI": None, "IV": None},
        "EXT-X-ALLOW-CACHE": False
    }
    parsed = urlparse(m3u8)
    ts = []
    if os.path.exists(m3u8):
        with open(m3u8, "r") as f:
            text = f.read().strip()
    else:
        r = requests.get(m3u8, timeout=5)
        text = r.text.strip()
    assert text.startswith("#EXTM3U") and text.endswith("#EXT-X-ENDLIST")
    lines = text.split()
    i = 0
    key = None
    while i < len(lines):
        line: str = lines[i].strip()
        if line.strip().startswith("#EXT"):
            if ":" in line:
                tag, *data = line.split(":")
                data = ':'.join(data)
            else:
                tag = line
            if tag.startswith("#EXTINF"):
                duration, title = data.split(",")
                duration = float(duration.strip())
                i += 1
                uri = lines[i].strip()
                ts.append((uri, duration))
            elif tag.startswith("#EXT-X-KEY"):
                for item in data.split(","):
                    key, value = item.split("=")
                    metadata["EXT-X-KEY"][key.strip()] = value.strip()
                uri = metadata["EXT-X-KEY"]["URI"].strip('"')
                uri = f"{parsed.scheme}://{parsed.netloc}{uri}"
                key = requests.get(uri, timeout=5).content
        else:
            pass

        i += 1
    cryptor = AES.new(key, AES.MODE_CBC, key) if key else None
    url = ts[0][0].strip("index0.ts")
    index = 0
    with open(filename, "wb+") as f:
        while True:
            try:
                content = requests.get(url+f"index{index}.ts", headers=headers, timeout=15).content
            except:
                break
            if cryptor is not None:
                content = cryptor.decrypt(content)
            f.write(content)
            f.flush()
            print(url+f"index{index}.ts")
            index += 1
            if index>20:
                break

if __name__ == "__main__":
    def parse_m3u8(vid: str):
        url = "https://www.rcdy002.com/api/getmovie"
        params = {
            "type": "1280", 
            "id": vid
        }
        headers = {
            "Referer": f"https://www.rcdy002.com/cn/movie/{vid}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
        }
        r = requests.get(url, params=params, headers=headers, timeout=3)
        m3u8 = "https://www.rcdy002.com" + r.json()["m3u8"]
        return m3u8

    vid = "6127d82505277b06ade2f323"
    m3u8 = parse_m3u8(vid)
    download_m3u8(m3u8, "董莉娜女烈试镜.mp4")
    # app = HLS("https://www.rcdy002.com/videos/202203/02/621f482086a8d370bf9c2c38/a88c7g/index.m3u8?random=BcgaGgA2G9dbC92187bF")
    # app.download("demo.mp4")
