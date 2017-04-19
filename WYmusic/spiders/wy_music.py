# coding: utf-8
import os
import scrapy
import base64
import logging
import json
import time
from Crypto.Cipher import AES


class NEMusicSpider(scrapy.Spider):
    name = 'NE_music'
    allowed_domains = ['music.163.com']
    start_urls = [
        'http://music.163.com/weapi/user/playlist?csrf_token='
    ]
    play_detail = 'http://music.163.com/api/playlist/detail?id={0}'
    comment_detail = 'http://music.163.com/weapi/v1/resource/comments/{0}?csrf_token='
    formdata = {
        'params': 'y27+XjSXQIQnlyqqZN4u6CPIIGILaSRIEzBOnGHSPwskrSusVO4felPDPF03ZfF7WZnr6PWWOJgRjtDOSnuPEB5v5chySMpbQ0e2yaJbrDolEZdP1s9oRJJTCbdu/ZyAC+LPd7NrT1NQeDvl/nGAV9/ExS78qcgYZZYLqEB+KPC6Y2At+ot3apqCpTDcEL5ypJWi7OQh+jsOC3nRLbgFrtrCTQM/1tBGAy2bmMuJKwY=',
        'encSecKey': 'dd3db45472a08c80d04f53ee62d4f04a7f80fbb1e383830bee6d3ea37fb5a39db207aa50c5be9e3dcb9b80ef7b55cf77a661f29115d2ae1a8d953d59fb02083cddb3198e9d5b18f4670aa29d1994f851794f17baae14ea9c0805f7ab35f91a58a38ed344a747cb495e731ab0feb5949f59962dd73af614198b9a11e97469bce4'
    }
    pw_formdata = {
        'params': 'MHxjLo97184Az8NvJQjmnjwsr7bfwgDZKVNCFC4LrAQJDX9+/D20wzG3hfbd0pdx+NeFithe1jKfmBEnlUYpbIZcNxMMrLyrRl44ic1nNJCrYZuCJU4q+L89FrzHZ2UqfpHUvUegN6+7Ew6efIdtKIjTBrt5BC9k3BD5+bYfEjt23o6ekrTT8W+dt79a3Jb8JjXsUV5zglQNaRxOiyn/fCJa6U15ght8IiUdeDfBCn4=',
        'encSecKey': '181aeff4e419a93abc2745678eff5b62f2711f69265accfbfe81affe7e6f3e024f691b1e64fae2a09051fd969cf66d79cc4cbde976a1a8108858a7b897ca2ca042ba102a61f8246cbfee36ceda6f1ba0af20ec35032b9d02c0c0c2f27b43781b28f216fd4c45c4cb644d56050c33dc52059406e4f47a4e56fad6df37deae4cb5'
    }
    headers = {
        'Referer': 'http://music.163.com/',
        'Cookie': 'appver=1.5.0.75771;'
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'

    user_header = {
        'Referer': 'http://music.163.com/user/home?id=30725209',
        'Cookie': 'appver=1.5.0.75771'
    }
    users_id = {
        'pw': '30725209',
        'ycw': '115179616'
    }
    user_comments = {}
    limit = 1000
    offset = 0

    def encrypt(self, text, secKey):
        cryptor = AES.new(secKey, 2, '0102030405060708')
        pad = 16 - len(text) % 16
        text = text + bytes(pad)
        ciphertext = cryptor.encrypt(text)
        ciphertext = base64.b64encode(ciphertext)
        return ciphertext

    def rsa_encrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = int(''.join([hex(ord(c))[2:] for c in text]), 16)**int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def createSecretKey(self, size):
        return (''.join(map(lambda xx: (hex(xx)[2:]), os.urandom(size))))[0:16]

    def paramsCreator(self, limit, offset):
        text = {
            'limit': limit,
            'offset': offset,
        }
        text = json.dumps(text)
        secKey = self.createSecretKey(16)
        logging.info('The secure key is: %s' % secKey)
        encSecKey = self.rsa_encrypt(text, self.pubKey, self.modulus)
        logging.info('The encrypted secure ket is: %s' % encSecKey)
        text = text.encode('utf-8')
        encText = self.encrypt(self.encrypt(text, self.nonce), secKey).decode('utf-8')
        logging.info('The encrypted text is: %s' % encText)
        params = {
            'params': encText,
            'encSecKey': encSecKey
        }

        return params

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.FormRequest(
                url=url,
                formdata=self.pw_formdata,
                headers=self.user_header,
                callback=self.parse
            )

    def parse(self, response):
        playlist = json.loads(response.text)['playlist']
        for play in playlist:
            if str(play['creator']['userId']) == self.users_id['pw']:
                play_id = play['id']
                logging.info('play list id is: %s' % play_id)
                yield scrapy.Request(
                    url=self.play_detail.format(play_id),
                    callback=self.parse_play
                )

    def parse_play(self, response):
        playinfo = json.loads(response.text)['result']
        logging.info('| The playlist name is: %s | This playlist has %d songs' % (playinfo['name'], playinfo['playCount']))
        songs = playinfo['tracks']

        for song in songs:
            commThread_id = song['commentThreadId']
            logging.info('| The song name is: %s | The comment thread id is: %s' % (song['name'], commThread_id))
            para = self.paramsCreator(1, 0)
            yield scrapy.FormRequest(
                url=self.comment_detail.format(commThread_id),
                headers=self.headers,
                formdata=para,
                callback=self.parse_song,
                meta={'song_name': song['name'], 'thread_id': commThread_id}
            )

    def parse_song(self, response):
        total_comments = json.dumps(response.text)['total']

        while self.offset < total_comments:
            time.sleep(2)
            logging.info(
                "正在查询歌曲: %s, 进度: %s/%s, 当前共找到评论: %d条" % (
                response.meta.get('song_name'), self.offset, total_comments, len(self.user_comments)))

            para = self.paramsCreator(self.limit, self.offset)
            try:
                yield scrapy.FormRequest(
                    url=self.comment_detail.format(response.meta.get('thread_id')),
                    headers=self.headers,
                    formdata=para,
                    callback=self.dumpdata
                )
            except:
                logging.info('网络异常,自动重试..')
                continue

            self.offset += self.limit

        logging.info("本次查询完毕")
        if self.user_comments:
            with open('pw_comment.json', 'w') as c:
                json.dump({response.meta.get('song_name'): self.user_comments}, c)
        self.user_comments = {}
        self.offset = 0

    def dumpdata(self, response):
        for comment in response['comments']:
            if comment['user']['userId'] == int(self.users_id['pw']):
                self.user_comments.update({comment['commentId']: comment['content']})
