#!/usr/bin/env python
# coding=utf-8

import oss2


class OSS(object):
    def __init__(self, ak, sk, endpoint, bucket):
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.bucket = bucket

    def download(self, remote, local):
        auth = oss2.Auth(self.ak, self.sk)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        try:
            bucket.get_object_to_file(remote, local)
            return True

        except oss2.exceptions.NoSuchKey as e:

            print('status={0}, request_id={1}'.format(e.status, e.request_id))
            return False
