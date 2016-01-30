#!/usr/bin/env python
# coding=utf-8

"""
Gearman Worker for Youku Upload (Python 2.7)
"""

import os
import json
import md5
import time
import urllib2
import gearman
import aliyun.oss as aliyun_oss
import conf.conf_oss as oss_conf
import conf.conf_gearman as gearman_conf
from youku import YoukuUpload
from youku.util import check_error, YoukuError


def http_post(url, data):
    """数据提交
    考虑到socket服务器可能会因为各种原因重启而无法收到消息的情况,
    我们使用python在worker里进行回调,从而保证不论socket服务器正常与否,都能拿到回调信息
    """
    try:
        data = json.dumps(data)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        response = urllib2.urlopen(req, data)
        return response.read()
    except urllib2.HTTPError, e:
        return e


def get_id():
    """生成随机id
    保证各个worker都使用不同的id,使用md5对当前时间进行加密
    """
    _now = str(time.time())
    _md5 = md5.new()
    _md5.update(_now)
    return _md5.hexdigest()


def remove_tmp(local_file_name):
    """删除本地临时文件
    抛出异常,不对异常做任何处理
    """
    try:
        # abs_path = os.path.abspath('.')
        # abs_path_local_key = os.path.join(abs_path,local_key_name)
        os.remove(local_file_name)
    except OSError as e:  # name the Exception `e`
        print "Failed with:", e.strerror  # look what it says
        print "Error code:", e.code


def youku_task(youku_conf, youku_upload, key_name):
    """优酷上传
    使用优酷sdk进行上传操作
    """
    print youku_conf
    print youku_upload
    print key_name

    key_fullname = key_name + '.mp4'
    youku = YoukuUpload(youku_conf["clientid"], youku_conf["ak"], key_fullname)
    try:
        video_id = youku.upload(youku_upload)
        success = {
            "code": "200",
            "msg": "upload success",
            "data": {
                "key": key_name,
                "videoid": str(video_id)
            }
        }
        remove_tmp(key_fullname)
        return success

    except YoukuError, e:
        failure = {
            "code": "500",
            "msg": str(e),
            "data": {
                "key": key_name
            }
        }
        remove_tmp(key_fullname)
        print failure
        return failure


def task_listener_upload(gearman_worker, gearman_job):
    """
    Task listener for upload (Gearman worker)
    """
    # String to dict
    data_json = json.loads(gearman_job.data)

    # Conf info for youku
    youku_conf = data_json.get("conf")
    youku_upload = data_json.get("youku")

    # bucket object key name
    key_name = youku_conf.get("keyname")

    # Conf oss & download file
    remote_key_name = 'user/dee/' + key_name
    local_key_fullname = key_name + '.mp4'

    # Oss download
    oss_sdk = aliyun_oss.OSS(oss_conf.ak, oss_conf.sk, oss_conf.endpoint, oss_conf.bucket)
    result_oss = oss_sdk.download(remote_key_name, local_key_fullname)

    if result_oss:
        result_youku = youku_task(youku_conf, youku_upload, key_name)
        http_post(youku_conf["callbackurl"], result_youku)
        return json.dumps(result_youku, indent=4)
    else:
        failure = {
            "code": "404",
            "msg": "oss key not found",
            "data": {
                "key": key_name
            }
        }
        remove_tmp(local_key_fullname)
        http_post(youku_conf["callbackurl"], failure)
        print failure
        return json.dumps(failure, indent=4)


# init gm_worker
gm_worker = gearman.GearmanWorker([gearman_conf.JOB_SERVER])

# gm_worker.set_client_id is optional
gm_worker.set_client_id('python-worker-' + get_id())

# add def for gm_worker to listen
gm_worker.register_task('upload', task_listener_upload)

# Enter our work loop and call gm_worker.after_poll() after each time we timeout/see socket activity
gm_worker.work()
