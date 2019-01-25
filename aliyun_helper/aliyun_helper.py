# -*- coding: utf-8 -*-

# Build-in Modules
import time
import json
import uuid

# Project Modules
from aliyun_common import AliyunCommon
from aliyun_oss import AliyunOSS

def get_config(c):
    return {
        'access_key_id'    : c.get('akId'),
        'access_key_secret': c.get('akSecret'),
    }

class AliyunHelper(object):
    def __init__(self, config=None):
        self.config        = config
        self.common_client = AliyunCommon(**get_config(config))
        self.oss_client    = AliyunOSS(**get_config(config))

    def verify(self):
        return self.common_client.verify()

    def common(self, product, timeout=3, **biz_params):
        return self.common_client.__getattr__(product)(timeout=timeout, **biz_params)

    def oss(self, method, timeout=3, **biz_params):
        return self.oss_client.__getattr__(method)(timeout=timeout, **biz_params)
