# -*- coding: utf-8 -*-

# Build-in Modules
import datetime
import base64
import hmac
import hashlib

# 3rd-part Modules
import requests

# Project Modules
from . import parse_response

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
OSS_API_CONFIG = {
    'top_domain'    : 'aliyuncs.com',
    'version'       : '',
    'port'          : 80,
    'protocol'      : 'http'
}

class AliyunOSS(object):
    '''
    Aliyun OSS HTTP API
    '''
    def __init__(self, access_key_id=None, access_key_secret=None, *args, **kwargs):
        self.access_key_id     = str(access_key_id)
        self.access_key_secret = str(access_key_secret)

        self._requests_session = requests.Session()

    def get_canonicalized_header_string(self, headers=None):
        canonicalized_header_string = ''

        if headers:
            oss_headers        = [(k.lower(), v) for k, v in headers.items() if k.lower().startswith('x-oss-')]
            sorted_oss_headers = sorted(oss_headers, key=lambda kv_pair: kv_pair[0])

            if sorted_oss_headers:
                canonicalized_header_string = '\n'.join(k + ':' + v for k, v in sorted_oss_headers) + '\n'

        return canonicalized_header_string

    def get_canonicalized_resource_string(self, bucket_name=None, object_name=None, sub_resource=None, query=None):
        canonicalized_resource_string = '/'

        if bucket_name:
            canonicalized_resource_string += bucket_name + '/'

            if object_name:
                canonicalized_resource_string += object_name

        if sub_resource:
            canonicalized_resource_string += '?' + sub_resource

        return canonicalized_resource_string

    def sign(self, req, canonicalized_header_string, canonicalized_resource_string):
        string_to_sign = '\n'.join([
            req.method.upper(),
            req.headers.get('content-md5', ''),
            req.headers.get('content-type', ''),
            req.headers.get('date', ''),
            canonicalized_header_string + canonicalized_resource_string
        ])
        h = hmac.new(self.access_key_secret, string_to_sign, hashlib.sha1)
        signature = base64.encodestring(h.digest()).strip()

        return signature

    def verify(self):
        status_code, _ = self.call('GET', 'oss-cn-hangzhou')
        return (status_code == 200)

    def call(self, method, region_id=None, bucket_name=None, object_name=None, sub_resource=None, query=None, body=None, headers=None, timeout=3):
        method = method.upper()

        region_id = region_id or 'oss-cn-hangzhou'

        if object_name and object_name.startswith('/'):
            object_name = object_name[1:]

        headers = headers or {}
        headers['date'] = datetime.datetime.utcnow().strftime(GMT_FORMAT)

        if body:
            if isinstance(body, unicode):
                body = body.encode('utf8')

            h = hashlib.md5()
            h.update(body)
            headers['content-md5'] = base64.encodestring(h.digest()).strip()

        canonicalized_header_string   = self.get_canonicalized_header_string(headers)
        canonicalized_resource_string = self.get_canonicalized_resource_string(bucket_name, object_name, sub_resource, query)

        domain = '{}.{}'.format(region_id, OSS_API_CONFIG['top_domain'])
        if bucket_name:
            domain = bucket_name + '.' + domain

        url = '{}://{}/{}'.format(OSS_API_CONFIG['protocol'], domain, object_name or '')

        if sub_resource:
            query = query or {}
            query[sub_resource] = ''

        req = requests.Request(method, url, params=query, data=body, headers=headers)
        prepared_req = self._requests_session.prepare_request(req)

        signature = self.sign(prepared_req, canonicalized_header_string, canonicalized_resource_string)
        prepared_req.headers['authorization'] = 'OSS {}:{}'.format(self.access_key_id, signature)

        resp = self._requests_session.send(prepared_req, timeout=timeout)
        parsed_resp = parse_response(resp)

        return resp.status_code, parsed_resp

    def __getattr__(self, method):
        method = method.upper()

        def f(timeout=3, **biz_params):
            kwargs = {
                'region_id'   : biz_params.get('RegionId'),
                'bucket_name' : biz_params.get('BucketName'),
                'object_name' : biz_params.get('ObjectName'),
                'query'       : biz_params.get('Query'),
                'sub_resource': biz_params.get('SubResource'),
                'body'        : biz_params.get('Body'),
                'headers'     : biz_params.get('Headers'),
            }
            return self.call(method, **kwargs)

        return f
