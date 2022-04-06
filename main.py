import json

import requests
from pprint import pprint


with open('token_vk.txt', 'r') as f:
    token_vk = f.read().strip()

with open('token_ya.txt', 'r') as f:
    token_ya = f.read().strip()


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photos(self, user_id=None):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'user_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'feed_type': 'photo',
            'photo_sizes': 1,
            'count': 5
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        photos_links = []
        likes = []
        for i in range(photos_params['count']):
            sizes = res['response']['items'][i]['sizes']
            for item in sizes:
                if 'w' in item.values():
                    photos_links.append(item['url'])
                    likes.append(res['response']['items'][i]['likes']['count'])
                # elif 'z' in item.values():
                #     photos_links.append(item['url'])
                #     likes.append(res['response']['items'][i]['likes']['count'])
                # Почему-то, когда я ввожу проверку на другие разрешения фото (на случай, если самого лучшего нет), например,
                # если нет w, то проверяю,есть ли z и т.д. Даже введение еще одного уровня elif приводит к ошибке:
                # counter out of range. Буду рада, если вы мне поможете.



        counter = 0

        info_file_content = [{}, {}, {}, {}, {}]

        for pic in photos_links:

            img = requests.get(pic)
            with open(f'photos_storage/{likes[counter]}.jpg', "wb") as file:
                file.write(img.content)
            info_file_content[counter]['file_name'] = f'{likes[counter]}.jpg'
            info_file_content[counter]['size'] = 'w'
            counter += 1

        with open('info.json', 'w') as file:
            json.dump(info_file_content, file)

        return photos_links, likes, info_file_content


class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }


    def get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': disk_file_path, 'overwrite': 'false'}
        response = requests.get(upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()


    def upload(self, file_path, disk_file_path):
        href_json = self.get_upload_link(disk_file_path=disk_file_path)
        href = href_json['href']
        response = requests.put(href, data=open(file_path, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print('Success')


vk_client = VkUser(token_vk, '5.131')
vk_client.get_photos()

with open('info.json') as file:
    pic_data = json.load(file)


uploader = YaUploader(token_ya)

for pic in pic_data:
    uploader.upload(f"photos_storage/{pic['file_name']}", f"course_project/{pic['file_name']}")
