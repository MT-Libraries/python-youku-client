#!/usr/bin/env python
# coding=utf-8

"""
Gearman Worker for Youku Upload (Python 2.7)
"""

import os
import json
import md5
import time
import gearman
import aliyun.oss as aliyun_oss
import conf.conf_oss as oss_conf
import conf.conf_gearman as gearman_conf
from youku import YoukuUpload
from youku.util import check_error, YoukuError


def get_id():
    """
    Generate md5 string as worker id
    Returns:
        STRING
    """
    _now = str(time.time())
    _md5 = md5.new()
    _md5.update(_now)
    return _md5.hexdigest()


def remove_tmp(local_key_name):
    """
    Remove tmp file and throw OSError
    Args:
        local_key_name:

    Returns:
        NONE
    """
    try:
        # abs_path = os.path.abspath('.')
        # abs_path_local_key = os.path.join(abs_path,local_key_name)    
        os.remove(local_key_name)
    except OSError as e:  # name the Exception `e`
        print "Failed with:", e.strerror  # look what it says
        print "Error code:", e.code


def youku_task(youku_conf, youku_upload, local_key_name):
    """
    Upload local file to Youku with Youku SDK
    """
    youku = YoukuUpload(youku_conf["clientid"], youku_conf["ak"], local_key_name)
    try:
        YOUKU_SUCCESS = {
            "code": "200",
            "info": "upload success"
        }
        youku.upload(youku_upload)
        remove_tmp(local_key_name)
        return YOUKU_SUCCESS

    except YoukuError, e:
        YOUKU_ERROR = {
            "code": "500",
            "msg": str(e)
        }
        print YOUKU_ERROR
        return YOUKU_ERROR


def task_listener_upload(gearman_worker, gearman_job):
    """
    Task listener for upload (Gearman worker)
    """
    # String to dict
    data_json = json.loads(gearman_job.data)

    # Conf info for youku
    youku_conf = {}
    youku_conf["clientid"] = data_json.get("clientid")
    youku_conf["ak"] = data_json.get("ak")
    youku_upload = data_json.get("youku")

    # Download key_name for oss                
    key_name = data_json.get("keyname")  # bucket object key name

    # Conf oss & download file  
    remote_key_name = 'user/dee/' + key_name
    local_key_name = key_name + '.mp4'

    # Oss download 
    oss_sdk = aliyun_oss.OSS(oss_conf.ak, oss_conf.sk, oss_conf.endpoint, oss_conf.bucket)
    result_oss = oss_sdk.download(remote_key_name, local_key_name)

    if result_oss['code'] == "404":
        print result_oss["msg"]
        return json.dumps(result_oss, indent=4)
    else:
        result_youku = youku_task(youku_conf, youku_upload, local_key_name)
        return json.dumps(result_youku, indent=4)


# init gm_worker
gm_worker = gearman.GearmanWorker([gearman_conf.JOB_SERVER])

# gm_worker.set_client_id is optional
gm_worker.set_client_id('python-worker-'+get_id())

# add def for gm_worker to listen
gm_worker.register_task('upload', task_listener_upload)

# Enter our work loop and call gm_worker.after_poll() after each time we timeout/see socket activity
gm_worker.work()
