#coding: utf-8
import requests
import json
# header
headers = {
    'Referer': 'http://music.163.com/',
    'Cookie': 'appver=1.5.0.75771;MUSIC_U=e954e2600e0c1ecfadbd06b365a3950f2fbcf4e9ffcf7e2733a8dda4202263671b4513c5c9ddb66f1b44c7a29488a6fff4ade6dff45127b3e9fc49f25c8de500d8f960110ee0022abf122d59fa1ed6a2;',
}
# post的数据
user_data = {
    'uid': '107948356',
    'type': '0',
    'params': 'eZMCYijT8paDO/VVaobvRprBwZdkmfGPDbX5d4DmDrs5ho4mmOtONLc81AcCOlU/59XkOYCYSt3rcbpkz8CMinOh4XhXiXsM8ZCdlCEmenm4HzbspZEE22cG7NZYGcGPCLTPb31dVOsmr56Yn7sMuyg9HhdZSL7vfv+aKjtfI93hm6Rxmms4LDfLh8qlNBuklK8BBa94MjYjgMZyLNGxrv9bqYI/7C0/GegiCdL0DM0=',
    'encSecKey': '13eb37e2074f4b346fb9f9716c4c8a4e11b0cdb6c6f3f8bd64ee1c7ae27fdf8314bb3926eb5effe0f892e5f0270314b18f99a513db7e96deb01efccf3ec3844c2fbcf99687794d9e4a206b3ac4a75a82d2f7d5f0fbe342e03779b3ee13ecf5e7d28da073271c1e637b50b09851ae11f0c7d3ea84fd3eafd89db9818923c713ca'
}
# 添加用户id、名字、以及喜欢的歌曲到user_love_songs数据库中
'params:eZMCYijT8paDO/VVaobvRprBwZdkmfGPDbX5d4DmDrs5ho4mmOtONLc81AcCOlU/59XkOYCYSt3rcbpkz8CMinOh4XhXiXsM8ZCdlCEmenm4HzbspZEE22cG7NZYGcGPCLTPb31dVOsmr56Yn7sMuyg9HhdZSL7vfv+aKjtfI93hm6Rxmms4LDfLh8qlNBuklK8BBa94MjYjgMZyLNGxrv9bqYI/7C0/GegiCdL0DM0='
'encSecKey:13eb37e2074f4b346fb9f9716c4c8a4e11b0cdb6c6f3f8bd64ee1c7ae27fdf8314bb3926eb5effe0f892e5f0270314b18f99a513db7e96deb01efccf3ec3844c2fbcf99687794d9e4a206b3ac4a75a82d2f7d5f0fbe342e03779b3ee13ecf5e7d28da073271c1e637b50b09851ae11f0c7d3ea84fd3eafd89db9818923c713ca'

def get_user_music(uid):
    data = []
    url = 'http://music.163.com/weapi/v1/play/record?csrf_token='
    user_data['uid'] = uid
    user_data['type'] = '0'
    response = requests.post(url, headers=headers, data=user_data)
    response = response.content
    json_text= json.loads(response.decode("utf-8"))
    try:
        json_all_data = json_text['allData']
        for json_music in json_all_data:
            json_song = json_music['song']
            json_song_name = json_song['name']   # 歌曲名字
            # print(json_song_name, end="")
            # print('---', end="")
            # 演唱者名字
            ar = json_song['ar']
            length = len(ar)
            songer_name = ''
            for songer in range(0, length):
                songer_name = songer_name + ar[songer]['name']
                # print(ar[songer]['name'], end="")
                # if (songer != length - 1):
                #     print('/', end="")
                # if (songer == length - 1):
                #     print('')
            # print(songer_name)
            song = json_song_name + '---' + songer_name
            data.append(song)
        print(data)
    except KeyError:
        print('id为', end="")
        print(uid, end="")
        print('的用户听歌排行不可查看~')
    except Exception as e:
        print('出现错误啦~错误是:', e)

# print(get_user_music('115179616'))
