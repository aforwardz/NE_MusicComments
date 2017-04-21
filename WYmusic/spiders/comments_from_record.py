# coding: utf-8
import scrapy
import base64
import logging
import json
import time
from Crypto.Cipher import AES

__author__ = 'https://github.com/IdiotYcw'
# Description：
# 输入用户id，获取用户所有时间听歌的record，然后爬取每首歌下该用户的评论
# 结果保存到文本


class NEMusicSpider(scrapy.Spider):
    name = 'NE_Record'
    allowed_domains = ['music.163.com']
    start_urls = [
        'http://music.163.com/weapi/v1/play/record?csrf_token='
    ]
    user_record = 'http://music.163.com/weapi/v1/play/record?csrf_token='
    user_playlist = 'http://music.163.com/weapi/user/playlist?csrf_token='
    play_detail = 'http://music.163.com/api/playlist/detail?id={0}'
    comment_detail = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{0}?csrf_token='

    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'

    # header
    header = {
        'Referer': 'http://music.163.com/',
        'Cookie': 'appver=1.5.0.75771;MUSIC_U=610b26c3be0b500a1a7000491af350e67479161dd6182f0b683865fb286441d9c959b8fe292055553e06215a23507ec0a70b41177f9edcea;',
    }

    # 不同用户可以在network formdata里copy一份
    user_para = {
        'uid': '',
        'type': '0',
        'params': 'eZMCYijT8paDO/VVaobvRprBwZdkmfGPDbX5d4DmDrs5ho4mmOtONLc81AcCOlU/59XkOYCYSt3rcbpkz8CMinOh4XhXiXsM8ZCdlCEmenm4HzbspZEE22cG7NZYGcGPCLTPb31dVOsmr56Yn7sMuyg9HhdZSL7vfv+aKjtfI93hm6Rxmms4LDfLh8qlNBuklK8BBa94MjYjgMZyLNGxrv9bqYI/7C0/GegiCdL0DM0=',
        'encSecKey': '13eb37e2074f4b346fb9f9716c4c8a4e11b0cdb6c6f3f8bd64ee1c7ae27fdf8314bb3926eb5effe0f892e5f0270314b18f99a513db7e96deb01efccf3ec3844c2fbcf99687794d9e4a206b3ac4a75a82d2f7d5f0fbe342e03779b3ee13ecf5e7d28da073271c1e637b50b09851ae11f0c7d3ea84fd3eafd89db9818923c713ca'
    }

    users_id = {
        'user_name': 'user_id'
    }

    songs_id = []
    user_comments = {}
    limit = 20  # 发现这里limit设置如果大于20，无论多少返回数据里只包含20条评论。。囧。。
    offset = 0

    # 这套加密参考https://github.com/wenhaoliang/netease-music-spider
    # 获取params
    def get_params(self, first_param, forth_param):
        iv = "0102030405060708"
        first_key = forth_param
        second_key = 16 * 'F'
        h_encText = self.AES_encrypt(first_param, first_key.encode(), iv.encode())
        h_encText = self.AES_encrypt(h_encText.decode(), second_key.encode(), iv.encode())
        return h_encText.decode()

    # 获取encSecKey
    def get_encSecKey(self):
        encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
        return encSecKey

    # 解AES秘
    def AES_encrypt(self, text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text.encode())
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text

    # 传入post数据
    def crypt_api(self, offset, limit):
        first_param = "{rid:\"\", offset:\"%s\", total:\"true\", limit:\"%s\", csrf_token:\"\"}" % (offset, limit)
        forth_param = "0CoJUm6Qyw8W8jud"
        params = self.get_params(first_param, forth_param)
        encSecKey = self.get_encSecKey()
        data = {
            "params": params,
            "encSecKey": encSecKey
        }
        return data

    """
    # 这套加密有点小问题，后面研究改进
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
            'rid': '',
            'limit': limit,
            'offset': offset,
            'total': 'true',
            'csrf_token': ''
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

    """

    def start_requests(self):
        uid = input('目标用户Id: ')
        self.user_para['uid'] = uid
        for url in self.start_urls:
            yield scrapy.FormRequest(
                url=url,
                formdata=self.user_para,
                headers=self.header,
                meta={'user': uid},
                callback=self.parse
            )

    def parse(self, response):
        records = json.loads(response.text)
        all_record = records['allData']
        logging.info('该用户有前%s条听歌排行记录' % len(all_record))
        # week_record = record['weekData']
        for record in all_record:
            song_id = record['song']['id']
            comm_url = self.comment_detail.format(song_id)
            para = self.crypt_api(0, 20)
            yield scrapy.FormRequest(
                url=comm_url,
                formdata=para,
                meta={'user': response.meta.get('user'), 'song_id': song_id},
                callback=self.parse_song
            )

    def parse_song(self, response):
        total_comments = json.loads(response.text)['total']
        user_id = response.meta.get('user')
        song_id = response.meta.get('song_id')

        logging.info('开始搜索歌曲: %s' % song_id)
        while self.offset < total_comments:
            time.sleep(1)

            para = self.crypt_api(self.offset, self.limit)
            try:
                yield scrapy.FormRequest(
                    url=self.comment_detail.format(song_id),
                    formdata=para,
                    meta={'song_id': song_id, 't_num': total_comments, 'offset': self.offset, 'uid': user_id},
                    callback=self.dumpdata
                )
            except:
                logging.info('网络异常,自动重试..')
                continue

            self.offset += self.limit

        logging.info("本次查询完毕")
        if self.user_comments:
            with open('comment_from_record.txt', 'w') as c:
                json.dump({song_id: self.user_comments}, c, ensure_ascii=False)
        self.user_comments = {}
        self.offset = 0

    def dumpdata(self, response):
        logging.info(
            "正在查询歌曲: %s, 进度: %s/%s, 当前共找到评论: %d条" % (
                response.meta.get('song_id'), response.meta.get('offset'),
                response.meta.get('t_num'), len(self.user_comments)))
        comments = json.loads(response.text)['comments']
        for comment in comments:
            logging.info('| %s : %s' % (comment['user']['nickname'], comment['content']))
            if comment['user']['userId'] == int(response.meta.get('uid')):
                self.user_comments.update({comment['commentId']: comment['content']})
