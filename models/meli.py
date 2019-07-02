 #!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import SafeConfigParser
from .ssl_helper import SSLAdapter
from urllib.parse import urlencode, unquote
import json
import os
import re
import requests
import ssl

auth={"MLA":"https://auth.mercadolibre.com.ar",
    "MLB":"https://auth.mercadolivre.com.br",
    "MCO":"https://auth.mercadolibre.com.co",
    "MCR":"https://auth.mercadolibre.com.cr",
    "MEC":"https://auth.mercadolibre.com.ec",
    "MLC":"https://auth.mercadolibre.cl",
    "MLM":"https://auth.mercadolibre.com.mx",
    "MLU":"https://auth.mercadolibre.com.uy",
    "MLV":"https://auth.mercadolibre.com.ve",
    "MPA":"https://auth.mercadolibre.com.pa",
    "MPE":"https://auth.mercadolibre.com.pe",
    "MRD":"https://auth.mercadolibre.com.do" 
}

class Meli(object):
    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = None

        parser = SafeConfigParser()
        parser.read(os.path.dirname(os.path.abspath(__file__))+'/config.ini')

        self._requests = requests.Session()
        try:
            self.SSL_VERSION = parser.get('config', 'ssl_version')
            self._requests.mount('https://', SSLAdapter(ssl_version=getattr(ssl, self.SSL_VERSION)))
        except:
            self._requests = requests

        self.API_ROOT_URL = parser.get('config', 'api_root_url')
        self.SDK_VERSION = parser.get('config', 'sdk_version')
        self.AUTH_URL = parser.get('config', 'auth_url')
        self.OAUTH_URL = parser.get('config', 'oauth_url')

    #AUTH METHODS
    def auth_url(self, site, redirect_URI):
        params = {'client_id':self.client_id,'response_type':'code','redirect_uri':redirect_URI}
        url = auth[site]  + '/authorization' + '?' + urlencode(params)
        return url

    def authorize(self, code, redirect_URI):
        params = { 'grant_type' : 'authorization_code', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'code' : code, 'redirect_uri' : redirect_URI}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(self.OAUTH_URL)

        response = self._requests.post(uri, params=urlencode(params), headers=headers)

        if response.status_code == requests.codes.ok:
            response_info = response.json()
            self.access_token = response_info['access_token']
            if 'refresh_token' in response_info:
                self.refresh_token = response_info['refresh_token']
            else:
                self.refresh_token = '' # offline_access not set up
                self.expires_in = response_info['expires_in']

            return self.access_token
        else:
            # response code isn't a 200; raise an exception
            response.raise_for_status()

    def get_refresh_token(self):
        if self.refresh_token:
            params = {'grant_type' : 'refresh_token', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'refresh_token' : self.refresh_token}
            headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
            uri = self.make_path(self.OAUTH_URL)

            response = self._requests.post(uri, params=urlencode(params), headers=headers, data=params)

            if response.status_code == requests.codes.ok:
                response_info = response.json()
                self.access_token = response_info['access_token']
                self.refresh_token = response_info['refresh_token']
                self.expires_in = response_info['expires_in']
                return self.access_token
            else:
                # response code isn't a 200; raise an exception
                response.raise_for_status()
        else:
            raise Exception("Offline-Access is not allowed.")

    # REQUEST METHODS
    def get(self, path, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(path)
        response = self._requests.get(uri, params=urlencode(params), headers=headers)
        return response

    def post(self, path, body=None, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.post(uri, data=body, params=urlencode(params), headers=headers)
        return response

    def upload(self, path, files, params={}):
        #headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'multipart/form-data'}
        headers = {}
        uri = self.make_path(path)
        response = requests.post(uri, files=files, params=urlencode(params), headers=headers)
        return response

    def put(self, path, body=None, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.put(uri, data=body, params=urlencode(params), headers=headers)
        return response

    def delete(self, path, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(path)
        response = self._requests.delete(uri, params=params, headers=headers)
        return response

    def options(self, path, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(path)
        response = self._requests.options(uri, params=urlencode(params), headers=headers)
        return response

    def make_path(self, path, params={}):
        # Making Path and add a leading / if not exist
        if not (re.search("^http", path)):
            if not (re.search("^\/", path)):
                path = "/" + path
            path = self.API_ROOT_URL + path
        if params:
            path = path + "?" + urlencode(params)
        return path
