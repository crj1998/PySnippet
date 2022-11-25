# -*- coding: utf-8 -*-
# @Author: Chen Renjie
# @Date:   2022-08-08 18:24:24
# @Last Modified by:   Chen Renjie
# @Last Modified time: 2022-08-08 19:25:06
 
import requests
 
 
"""
https://siwazyw.c
 
ac={list|videolist}&t={type_id}&pg={page}&wd={word}
"""
 
class CMS(object):
    def __init__(self, root, headers):
        self.root = root
        self.sess = requests.Session()
        self.sess.headers.update(headers)
        self.category = None
 
    def _get(self, params=None, timeout=3):
        params = params or {}
        r = self.sess.get(self.root, params=params, timeout=timeout)
        assert r.status_code == 200, f"Illegal status code {r.status_code}"
        ret = r.json()
        assert ret["code"] == 1, ret["msg"]
        return ret
 
    def home(self):
        ret = self._get({})
        print(f"Total: {ret['total']} Page: {ret['page']}/{ret['pagecount']}")
        self.category = ret["class"]
        for item in self.category:
            print(item["type_id"], item["type_name"])
 
    def search(self, wd):
        ret = self._get({"wd": wd})
        print(f"Total: {ret['total']} Page: {ret['page']}/{ret['pagecount']}")
        for item in ret["list"]:
            print(item["vod_id"], item["vod_time"], item["type_name"], item["vod_name"])
 
    def detail(self, vid):
        ret = self._get({"ac": "videolist", "ids": vid})
        metadata = ret["list"][0]
        print(metadata["vod_time"], metadata["vod_name"], metadata["vod_pic"], metadata["vod_play_url"].split("$")[-1])
 
        # print(ret)
 
if __name__ == '__main__':
    siwazyw = "https://siwazyw.cc/api.php/provide/vod/at/json/"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    app = CMS(siwazyw, headers)
    # app.home()
    app.search("slut")
    # app.detail(35190)