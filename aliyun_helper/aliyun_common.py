# -*- coding: utf-8 -*-

# Build-in Modules
import time
import uuid
import base64
import hmac
import hashlib

# 3rd-part Modules
import requests

# Project Modules
from . import percent_encode, parse_response

PRODUCT_API_CONFIG_MAP = {
    'ecs': {
        'domain'  : 'ecs.aliyuncs.com',
        'version' : '2014-05-26',
        'port'    : 80,
        'protocol': 'http'
    },
    'rds': {
        'domain'  : 'rds.aliyuncs.com',
        'version' : '2014-08-15',
        'port'    : 80,
        'protocol': 'http'
    },
    'drds': {
        'domain'  : 'drds.aliyuncs.com',
        'version' : '2015-04-13',
        'port'    : 80,
        'protocol': 'http'
    },
    'slb': {
        'domain'  : 'slb.aliyuncs.com',
        'version' : '2014-05-15',
        'port'    : 80,
        'protocol': 'http'
    },
    'ess': {
        'domain'  : 'ess.aliyuncs.com',
        'version' : '2014-08-28',
        'port'    : 80,
        'protocol': 'http'
    },
    'bss': {
        'domain'  : 'bss.aliyuncs.com',
        'version' : '2014-07-14',
        'port'    : 443,
        'protocol': 'https'
    },
    'mts': {
        'domain'  : 'mts.aliyuncs.com',
        'version' : '2014-06-18',
        'port'    : 80,
        'protocol': 'http'
    },
    'yundun': {
        'domain'  : 'yundun.aliyuncs.com',
        'version' : '2014-09-24',
        'port'    : 80,
        'protocol': 'http'
    },
    'cdn': {
        'domain'  : 'cdn.aliyuncs.com',
        'version' : '2014-11-11',
        'port'    : 80,
        'protocol': 'http'
    },
    'ram': {
        'domain'  : 'ram.aliyuncs.com',
        'version' : '2015-05-01',
        'port'    : 443,
        'protocol': 'https'
    },
    'sts': {
        'domain'  : 'sts.aliyuncs.com',
        'version' : '2015-04-01',
        'port'    : 80,
        'protocol': 'http'
    },
    'dysms': {
        'domain'  : 'dysmsapi.aliyuncs.com',
        'version' : '2017-05-25',
        'port'    : 80,
        'protocol': 'http'
    },
    'dyvms': {
        'domain'  : 'dyvmsapi.aliyuncs.com',
        'version' : '2017-05-25',
        'port'    : 80,
        'protocol': 'http'
    },
}

class AliyunCommon(object):
    '''
    Aliyun common HTTP API
    '''
    def __init__(self, access_key_id=None, access_key_secret=None, *args, **kwargs):
        self.access_key_id     = str(access_key_id)
        self.access_key_secret = str(access_key_secret)

    def sign(self, params_to_sign):
        canonicalized_query_string = ''

        sorted_params = sorted(params_to_sign.items(), key=lambda kv_pair: kv_pair[0])
        for k, v in sorted_params:
            canonicalized_query_string += percent_encode(k) + '=' + percent_encode(v) + '&'

        canonicalized_query_string = canonicalized_query_string[:-1]

        string_to_sign = 'POST&%2F&' + percent_encode(canonicalized_query_string)

        h = hmac.new(self.access_key_secret + "&", string_to_sign, hashlib.sha1)
        signature = base64.encodestring(h.digest()).strip()

        return signature

    def verify(self):
        status_code, _ = self.call_ecs(Action='DescribeRegions')
        return (status_code == 200)

    def call(self, domain, version, port=80, protocol='http', timeout=3, **biz_params):
        api_params = {
            'Format'          : 'json',
            'Version'         : version,
            'AccessKeyId'     : self.access_key_id,
            'SignatureVersion': '1.0',
            'SignatureMethod' : 'HMAC-SHA1',
            'SignatureNonce'  : str(uuid.uuid4()),
            'Timestamp'       : time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            'partner_id'      : '1.0',
        }

        api_params.update(biz_params)
        api_params['Signature'] = self.sign(api_params)

        url = '{}://{}:{}/'.format(protocol, domain, port)

        resp = requests.post(url, data=api_params, timeout=timeout)
        parsed_resp = parse_response(resp)

        return resp.status_code, parsed_resp

    def __getattr__(self, product):
        api_config = PRODUCT_API_CONFIG_MAP.get(product)

        if not api_config:
            raise Exception('Unknow Aliyun product API config. Please use `call()` with full API configs.')

        domain   = api_config.get('domain')
        version  = api_config.get('version')
        port     = api_config.get('port')
        protocol = api_config.get('protocol')

        def f(timeout=3, **biz_params):
            return self.call(domain=domain, version=version, port=port, protocol=protocol, timeout=timeout, **biz_params)

        return f