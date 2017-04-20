# coding: utf-8
import os
import scrapy
import base64
import logging
import json
import time
from Crypto.Cipher import AES

class test(scrapy.Spider):
    name = 'test_music'
    allowed_domains = ['music.163.com']
    start_urls = [
        'http://music.163.com/weapi/v1/resource/comments/{0}?csrf_token='
    ]
    play_detail = 'http://music.163.com/api/playlist/detail?id={0}'
    comment_detail = 'http://music.163.com/weapi/v1/resource/comments/{0}?csrf_token='

    headers = {
        'Referer': 'http://music.163.com/',
        'Cookie': 'appver=1.5.0.75771;'
    }
    s_data = {
       'params': '00HMk0LndpPXgkSFGV4M+RKZlK5SfYc2HZPsRMALafmFVXvu6+qeea8E8YiQO5cbfmkiD06t7xrOFsi6gdcC+EwGzMtgA+y68+gw+YzgX6oIyzLH5/jcD2M8RLJanfFv1AKjvu2wn3878Eyb1RSs2I1sYfhL+cytQO6jj0BCtO9xR0oSgwYQhWjZAwnv5G9qE4VlnVdxOX6jqTpQhzUXDmghtmJgeym6n7H4E53jwzo=',
        'encSecKey': 'dd4c44b80219e12f6d02bf1aeff546823379d1737bcaee077b8c3b10b55730b62e8152f779830f2330f4d3c8a164ab03d687af56e64a9cc697d3e38578997778b0386040d636a198c7e01fec9c0cd51bcc80449dc35758ce666f6c5fe22c6b3aabe0e56873018388dcc54e18ed9949078f2839962841d254c78bc8da7a6037b3'
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'

    def encrypt(self, text, secKey):
        cryptor = AES.new(secKey, 2, '0102030405060708')
        pad = 16 - len(text) % 16
        text = text + bytes(pad)
        ciphertext = cryptor.encrypt(text)
        ciphertext = base64.b64encode(ciphertext)
        return ciphertext

    def rsa_encrypt(self, text, pubKey, modulus):
        text = text[::-1]
        logging.info(text)
        rs = int(''.join([hex(ord(c))[2:] for c in text]), 16)**int(pubKey, 16) % int(modulus, 16)
        logging.info(rs)
        return format(rs, 'x').zfill(256)

    def get_encSecKey(self):
        return 'dd4c44b80219e12f6d02bf1aeff546823379d1737bcaee077b8c3b10b55730b62e8152f779830f2330f4d3c8a164ab03d687af56e64a9cc697d3e38578997778b0386040d636a198c7e01fec9c0cd51bcc80449dc35758ce666f6c5fe22c6b3aabe0e56873018388dcc54e18ed9949078f2839962841d254c78bc8da7a6037b3'

    def createSecretKey(self, size):
        return (''.join(map(lambda xx: (hex(xx)[2:]), os.urandom(size))))[0:16]

    def paramsCreator(self, limit, offset):
        text = {
            'rid': 'R_SO_4_25731497',
            'limit': limit,
            'offset': offset,
            'total': 'true',
            'csrf_token': ''
        }
        text = json.dumps(text)
        logging.info('text is: %s' % text)
        secKey = self.createSecretKey(16)
        logging.info('The secure key is: %s' % secKey)
        text_en = text.encode('utf-8')
        encText = self.encrypt(self.encrypt(text_en, self.nonce), secKey).decode('utf-8')
        logging.info('The encrypted text is: %s' % encText)
        encSecKey = self.rsa_encrypt(text, self.pubKey, self.modulus)
        logging.info('The encrypted secure ket is: %s' % encSecKey)
        params = {
            'params': encText,
            'encSecKey': encSecKey
        }

        return params

    def start_requests(self):

        thid = 'R_SO_4_25731497'
        para = self.paramsCreator('1000', '0')
        for url in self.start_urls:
            yield scrapy.FormRequest(
                url=url.format(thid),
                formdata=para,
                headers=self.headers,
                callback=self.parse
            )

    def parse(self, response):
        print(response.text)