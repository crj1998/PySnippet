# -*- coding: utf-8 -*-
# @Author: Chen Renjie
# @Date:   2022-07-22 19:47:54
# @Last Modified by:   Chen Renjie
# @Last Modified time: 2022-08-01 17:57:36
 
import os
import magic
import boto3
import requests
# pip install python-magic-bin==0.4.14
 
 
 
class S3(object):
    def __init__(self, ak, sk, endpoint_url):
        self.ak = ak
        self.sk = sk
        self.endpoint_url = endpoint_url
 
        self.client = boto3.client(
            's3',
            aws_access_key_id = ak,
            aws_secret_access_key = sk,
            endpoint_url = endpoint_url,
            region_name='cn',
        )
 
    # 确认存储桶
    def head_bucket(self, bucket):
        try:
            r = self.client.head_bucket(Bucket=bucket)
            # print(r['RetryAttempts'])
            return True
        except Exception as e:
            print(e)
            return False
 
    # 列举存储桶 '%Y-%m-%d %H:%M:%S'
    def list_buckets(self, fmt=None):
        r = self.client.list_buckets()
        owner = f"{r['Owner']['DisplayName']}({r['Owner']['ID']})"
        if isinstance(fmt, str):
            t = lambda x: x.strftime(fmt)
        else:
            t = lambda x: x
             
        buckets = [(b['Name'], t(b['CreationDate'])) for b in r['Buckets']]
        return buckets, owner
 
    # 创建存储桶
    def create_bucket(self, bucket):
        assert not self.head_bucket, "Bucket already exists"
        raise NotImplementedError
 
    # 删除存储桶 
    def delete_bucket(self, bucket):
        assert self.head_bucket, "Bucket not exists"
        raise NotImplementedError
         
    def get_bucket_acl(self, bucket):
        r = self.client.get_bucket_acl(
            Bucket=bucket
        )
        permission = r['Grants'][0]['Permission']
        return permission
 
    def list_objects(self, bucket):
        raise NotImplementedError
 
    def head_object(self, bucket, key):
        try:
            r = self.client.head_object(Bucket=bucket, Key=key)
            # print(r['RetryAttempts'])
            return True
        except Exception as e:
            print(e)
            return False
         
    def get_object(self, bucket, key):
        r = self.client.get_object(Bucket=bucket, Key=key)
        body = r['Body'].read()
        return body
 
    def put_object(self, bucket, key, body):
        assert not self.head_object(bucket, key)
        r = self.client.put_object(
            Bucket=bucket, Key=key, Body=body
            # ContentType 
        )
        print(r)
        return True
 
    def delete_object(self, bucket, key):
        assert self.head_object(bucket, key)
        r = self.client.delete_object(Bucket=bucket, Key=key)
        return True
 
    def download(self, bucket, key, f):
        assert isinstance(f, (str, bytes))
        if isinstance(f, str):
            self.client.download_file(Bucket=bucket, Key=key, Filename=f)
        elif isinstance(f, bytes):
            self.client.download_fileobj(Bucket=bucket, Key=key, Fileobj=f)
        else:
            pass
        # with open(filename, 'wb') as data:
        #     self.client.download_fileobj(Bucket=bucket, Key=key, Fileobj=data)
     
    def upload(self, f, bucket, key):
        assert isinstance(f, (str, bytes))
        if isinstance(f, str):
            self.client.upload_file(Filename=f, Bucket=bucket, Key=key, ExtraArgs={'ContentType': magic.from_file(f, mime=True)})
        elif isinstance(f, bytes):
            self.client.upload_fileobj(Fileobj=f, Bucket=bucket, Key=key, ExtraArgs={'ContentType': magic.from_buffer(f, mime=True)})
        else:
            return False
        return True
 
    def upload_folder(self, root, bucket, prefix=None):
        for f in os.listdir(root):
            key = f if prefix is None else os.path.join(prefix, f)
            key = "/".join(key.split(os.sep))
            r = self.upload(os.path.join(root, f), bucket, key)
            print(key, r)
 
 
    def transfer(self, url, bucket, filename=None, prefix=None):
        filename = filename or os.path.basename(url)
        key = filename if prefix is None else os.path.join(prefix, filename)
        assert not self.head_object(bucket, key), f"file {key} exists!"
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
        body = r.content
        content_type = r.headers["Content-Type"]
        r = self.client.put_object(
            Bucket=bucket, Key=key, Body=body,
            ContentType=content_type
        )
        print(r['ETag'], r['VersionId'])
 
 
"""土星云
 
https://saturncloud.com.cn/
"""
 
class Saturn(S3):
    def __init__(self, ak, sk, endpoint_url="https://s3.cn-global-0.xxyy.co:16000"):
        super(Saturn, self).__init__(ak, sk, endpoint_url)
 
    def list_objects(self, name):
        # assert self.head_bucket(name), "Bucket not exists"
        r = self.client.list_objects_v2(
            Bucket=name,
            # Delimiter='/',
            # MaxKeys=2,
        )
        print(r)
 
    def create_bucket(self, name):
        pass
 
    def head_object(self, bucket, key):
        r = self.client.head_object(Bucket=bucket, Key=key)
        print(r)
 
 
 
 
class Qiniu(S3):
    def __init__(self, ak, sk, endpoint_url="https://s3.cn-global-0.xxyy.co:16000"):
        super(Qiniu, self).__init__(ak, sk, endpoint_url)
 
    def list_objects(self, bucket):
        assert self.head_bucket(bucket), "Bucket not exists"
        r = self.client.list_objects_v2(
            Bucket=bucket,
            # Delimiter='/',
            # MaxKeys=2,
        )
        contents = [(c['Key'], c['Size']) for c in r["Contents"]]
        assert len(contents) == r["KeyCount"]
        return contents
 
    def create_bucket(self, bucket):
        pass
 
class BackBlaze(S3):
    def __init__(self, ak, sk, endpoint_url="https://s3.cn-global-0.xxyy.co:16000"):
        super(BackBlaze, self).__init__(ak, sk, endpoint_url)
 
    def list_objects(self, bucket, prefix=""):
        assert self.head_bucket(bucket), "Bucket not exists"
        r = self.client.list_objects_v2(
            Bucket=bucket,
            # Delimiter='/',
            # MaxKeys=2,
            Prefix=prefix
        )
        contents = [(c['Key'], c['Size']) for c in r["Contents"]]
        assert len(contents) == r["KeyCount"]
        return contents
 
if __name__ == '__main__':

    print(boto3.__version__)

    ApplicationKeyID = ""    # AK
    ApplicationKey = ""    # SK
    EndpointURL = "https://s3.us-west-004.backblazeb2.com" 
 
    app = BackBlaze(ApplicationKeyID, ApplicationKey, EndpointURL)
    res = app.list_buckets('%Y-%m-%d %H:%M:%S')
    print(res)
 
    # res = app.get_bucket_acl('meetslut')
    # print(res)
 
    # res = app.list_objects('meetslut', "REIPON")
    # # print(res)
    # for name, size in res:
    #     print("https://img.meetslut.ml/"+name)
 
    # app.transfer(url, 'meetslut')
    # 
    # app.upload_folder("D:\\BaiduYunDownload\\LeakedJP REIPON", "meetslut", "REIPON")
