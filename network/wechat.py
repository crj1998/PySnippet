import time
import requests

class WeChat:
    def __init__(self, CORPID, CORPSECRET):
        self.CORPID = CORPID  #企业ID，在管理后台获取
        self.CORPSECRET = CORPSECRET#自建应用的Secret，每个自建应用里都有单独的secret
        self.AGENTID = '1000002'  #应用ID，在后台应用中获取
        self.TOUSER = "ChenRenJie"  # 接收者用户名,多个用户用 |分割，@all表示全体用户
        self.TOPARY = "2"    #部门ID
        self.CONF = "access_token.conf"

    def _get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {
            'corpid': self.CORPID,
            'corpsecret': self.CORPSECRET,
        }
        r = requests.post(url, params=params)
        return r.json()["access_token"]

    def get_access_token(self):
        cur_time = time.time()
        try:
            with open(self.CONF, "r") as f:
                t, access_token = f.read().split()
        except:
            with open(self.CONF, "w") as f:
                access_token = self._get_access_token()
                f.write('\t'.join([str(cur_time), access_token]))
                return access_token
        else:
            if cur_time - float(t) < 7260:
                return access_token
            else:
                with open(self.CONF, 'w') as f:
                    access_token = self._get_access_token()
                    f.write('\t'.join([str(cur_time), access_token]))
                    return access_token
    
    def upload_media(self, path, dtype="file"):
        assert dtype in ["image", "voice", "video", "file"]
        url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload"
        params = {
            "access_token": self.get_access_token(),
            "type": dtype
        }
        files = {"media": open(path, "rb")}
        r = requests.post(url, params=params, files=files)
        return r.json()["media_id"]

    def send_message(self, payload):
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
        params = {
            "access_token": self.get_access_token()
        }
        r = requests.post(url, params=params, json=payload)
        return r.json()["errmsg"]

    def send_text(self, text):
        data = {
            "msgtype": "text",
            "touser": self.TOUSER,
            "agentid": self.AGENTID,
            "text": {
                "content": text
            },
            "safe": "0"
        }
        self.send_message(data)

    def send_media(self, msgtype, path):
        data = {
            "msgtype": msgtype,
            "touser": self.TOUSER,
            "agentid": self.AGENTID,
            msgtype: {
                "media_id" : self.upload_media(path, msgtype)
            },
            "safe": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }

        self.send_message(data)
    
    def send_textcard(self, textcard):
        data = {
            "msgtype": "textcard",
            "touser": self.TOUSER,
            "agentid": self.AGENTID,
            "textcard" : textcard,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        self.send_message(data)
    
    def send_markdown(self, content):
        data = {
            "msgtype": "markdown",
            "touser": self.TOUSER,
            "agentid": self.AGENTID,
            "markdown": {
                "content": content
            },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        self.send_message(data)

if __name__ == "__main__":
    wx = WeChat()
    # wx.send_media("image", "cat.png")
    # wx.send_media("file", "requirements.txt")

    wx.send_text("Test "+time.strftime("%Y-%m-%d %H:%M:%S"))

    description = f"""<div class='gray'>{time.strftime('%Y-%m-%d %H:%M:%S')}</div> <div class='normal'> 价格已经溢出 </div> <div class='highlight'> 请尽快操作 </div>
    """
    textcard = {
        "title" : "预警通知",
        "description" : description,
        "url" : "https://crj1998.ml/",
        "btntxt": "详情"
    }
    # wx.send_textcard(textcard)

    t = time.strftime("%Y-%m-%d %H:%M:%S")
    content = f"""
    > **Epoch 1**
    > Clean: <font color='info'> 70 %</font> Robust: <font color='warning'> 42 %</font>
    <font color='comment'>{t}</font> from Colab
    """
    wx.send_markdown(content)





