#!/usr/bin/env python
# coding=utf-8

from youku import YoukuUpload
import aliyun.oss as aliyun_oss
import conf.conf_oss as oss_conf
import conf.conf_youku as youku_conf
from youku.util import check_error, YoukuError


def main():
    file = "00d64e1f7701c62b5ba6123303ca5961"

    def download():
        oss_sdk = aliyun_oss.OSS(oss_conf.ak, oss_conf.sk, oss_conf.endpoint, oss_conf.bucket)
        result = oss_sdk.download('user/dee/' + file, file + '.mp4')
        print result

    def upload():

        file_info = {
            'title': u'优酷合作测试-VID',
            'tags': 'other',
            'description': 'Polymer video #7'
            # 'category': 'Tech'
        }

        youku = YoukuUpload(youku_conf.CLIENT_ID, youku_conf.ACCESS_TOKEN, file + ".mp4")

        # youku.create(youku.prepare_video_params(**params))
        # youku.create_file()
        # youku.upload_slice()
        # youku.check()
        # youku.commit()
        # youku.cancel()
        # youku.spec()

        try:
            vid = youku.upload(file_info)
            print vid
        except YoukuError, e:
            print e

    download()
    upload()


if __name__ == '__main__':
    main()
