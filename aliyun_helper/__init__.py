# -*- coding: utf-8 -*-

# Build-in Modules
import urllib
import json

# 3rd-part Modules
import xmltodict

def percent_encode(s):
    # I fell sick...
    if isinstance(s, unicode):
        s = s.encode('utf8')
    else:
        s = str(s).decode('utf8').encode('utf8')

    encoded = urllib.quote(s, '')
    encoded = encoded.replace('+', '%20')
    encoded = encoded.replace('*', '%2A')
    encoded = encoded.replace('%7E', '~')

    return encoded

def parse_response(response):
    resp_content_type = response.headers.get('content-type').lower().split(';')[0].strip()
    if resp_content_type == 'application/json':
        return response.json()

    elif resp_content_type == 'text/xml':
        return xmltodict.parse(response.text)

    else:
        try:
            return json.loads(response.text)

        except ValueError:
            try:
                return xmltodict.parse(response.text)

            except xmltodict.expat.ExpatError:
                return response.text

            except:
                raise

        except:
            raise

from aliyun_helper  import AliyunHelper
