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
        'params': 'I3XU4fuWrQrbJbuewnr4U9ZLNxLjcaWNP4pxlQ1neAPheiB59ejRj6iYfMtg9L9PgxKyiYrpxE4F1TcixETj/3Pgzr/REiKc/owLh4ZoiR4ir9lKYu7dgXLfT26b9v1gEi/z6C/bJhPxKRObBwBwQ0xnQaR7aj6CAfAdppRcTnWCi7ldGHWjoJulmPfa0FLdpH1xmZ/i61yZHAwKULTfO7V123jzmtAypYySLEwbzyA=',
        'encSecKey': '4c12ccb3f09b8fba71a264c76874fb4e38322b271f55cd81e8732a8bf99d1d165ebfd4095f651d8bd1279a3c5d314f156b9257a04ba4f4ad3027a5a3952408646ea6da183f0f8bd342e8b42ebf31af4889932f76daeb26df07df9a40b33bb73019f8e9fa12d0aa5c0154bbe807cbfbb16ed121c82fb2a02dca13bb442b24d84e'
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

    text = {
        'uid': '115179616',
        'type': '0'
    }

    def encrypt(self, text, secKey):
        cryptor = AES.new(secKey, 2, '0102030405060708')
        text = text.encode('utf-8')
        pad = 16 - len(text) % 16
        text = text + (b'0' * pad)
        ciphertext = cryptor.encrypt(text)
        ciphertext = base64.b64encode(ciphertext)
        return ciphertext

    def rsa_encrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = int(text.encode('hex'), 16)**int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def createSecretKey(self, size):
        return os.urandom(size)
        # return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

    def start_requests(self):
        text = {
            'uid': '115179616',
            'type': '0'
        }
        text = json.dumps(text)
        secKey = self.createSecretKey(16)
        encText = self.encrypt(text, secKey)
        encSecKey = self.rsa_encrypt(text, self.pubKey, self.modulus)
        formdata = {
            'params': encText,
            'encSecKey': encSecKey
        }
        for url in self.start_urls:
            yield scrapy.FormRequest(
                url=url,
                formdata=formdata,
                headers=self.headers,
                callback=self.parse
            )

    def parse(self, response):
        playlist = json.loads(response.text)['playlist']
        logging.info(playlist)
        for play in playlist.items():
            play_id = play['id']
            yield scrapy.Request(
                url=self.play_detail.format(play_id),
                callback=self.parse_play
            )

    def parse_play(self, response):
        playinfo = json.loads(response.text)['result']
        logging.info('| The playlist name is: %s | This playlist has %d songs' % (playinfo['name'], playinfo['playCount']))
        songs = playinfo['tracks']
        for song in songs.items():
            commThread_id = song['commentThreadId']
            logging.info('| The song name is: %s and the threadId is %s' % (song['name'], commThread_id))
