# coding: utf-8
import os
import scrapy
import base64
import  logging
import json
from Crypto.Cipher import AES


class NEMusicSpider(scrapy.Spider):
    name = 'NE_music'
    allowed_domains = ['music.163.com']
    start_urls = [
        'http://music.163.com/weapi/user/playlist?csrf_token='
    ]
    play_detail = 'http://music.163.com/api/playlist/detail?id={0]'
    comment_detail = 'http://music.163.com/weapi/v1/resource/comments/{0}?csrf_token='
    formdata = {
        'params': 'y27+XjSXQIQnlyqqZN4u6CPIIGILaSRIEzBOnGHSPwskrSusVO4felPDPF03ZfF7WZnr6PWWOJgRjtDOSnuPEB5v5chySMpbQ0e2yaJbrDolEZdP1s9oRJJTCbdu/ZyAC+LPd7NrT1NQeDvl/nGAV9/ExS78qcgYZZYLqEB+KPC6Y2At+ot3apqCpTDcEL5ypJWi7OQh+jsOC3nRLbgFrtrCTQM/1tBGAy2bmMuJKwY=',
        'encSecKey': 'dd3db45472a08c80d04f53ee62d4f04a7f80fbb1e383830bee6d3ea37fb5a39db207aa50c5be9e3dcb9b80ef7b55cf77a661f29115d2ae1a8d953d59fb02083cddb3198e9d5b18f4670aa29d1994f851794f17baae14ea9c0805f7ab35f91a58a38ed344a747cb495e731ab0feb5949f59962dd73af614198b9a11e97469bce4'
    }
    header = {
        'Referer': 'http://music.163.com/',
        'Cookie': 'appver=1.5.0.75771;MUSIC_U=610b26c3be0b500a96e90bed695581a0fc5d29359659ea311118394dcbecacb643e774dc49ad12964cb2fd59860e912da70b41177f9edcea'
    }
    headers = {
        'Referer': 'http://music.163.com/',
        'Cookie': 'appver=1.5.0.75771;'
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'

    user_header = {
        'Referer': 'http://music.163.com/user/home?id=115179616',
        'Cookie': 'appver=1.5.0.75771'
    }
    text = {
        'uid': '115179616',
        'offset': '0'
    }

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

    def start_requests(self):
        text = {
            'uid': '115179616',
            'offset': '0',
            'limit': '20',
            'csrf_token': 'de095a228434c3da0a47c5a0ffa57d91'
        }
        text = json.dumps(text)
        secKey = self.createSecretKey(16)
        logging.info('The secure key is: %s' % secKey)
        encSecKey = self.rsa_encrypt(text, self.pubKey, self.modulus)
        logging.info('The encrypted secure ket is: %s' % encSecKey)
        text = text.encode('utf-8')
        encText = self.encrypt(self.encrypt(text, self.nonce), secKey).decode('utf-8')
        logging.info('The encrypted text is: %s' % encText)
        print(len(encText), len(encSecKey))
        formdata = {
            'params': encText,
            'encSecKey': encSecKey
        }
        for url in self.start_urls:
            yield scrapy.FormRequest(
                url=url,
                formdata=formdata,
                headers=self.user_header,
                callback=self.parse
            )

    def parse(self, response):
        """
        playlist = json.loads(response.text)['playlist']
        logging.info(playlist)
        for play in playlist.items():
            play_id = play['id']
            yield scrapy.Request(
                url=self.play_detail.format(play_id),
                callback=self.parse_play
            )
        """
        print(response.text)

    def parse_play(self, response):
        playinfo = json.loads(response.text)['result']
        logging.info('| The playlist name is: %s | This playlist has %d songs' % (playinfo['name'], playinfo['playCount']))
        songs = playinfo['tracks']
        for song in songs.items():
            commThread_id = song['commentThreadId']
            logging.info('| The song name is: %s and the threadId is %s' % (song['name'], commThread_id))
