# -*- coding: utf-8 -*-

import json

from aliyun_helper import AliyunHelper

def main():
    # Create client helper
    client_helper = AliyunHelper({
        'akId'    : 'your_ak_id',
        'akSecret': 'your_ak_secret',
    })

    # Get ECS list
    status_code, api_res = client_helper.common('ecs', Action='DescribeInstances', RegionId='cn-shanghai')
    print json.dumps(api_res, indent=2)

    # Get OSS Bucket list
    status_code, api_res = client_helper.oss('GET')
    print json.dumps(api_res, indent=2)

if __name__ == '__main__':
    main()