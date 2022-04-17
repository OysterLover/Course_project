import json
import requests
from pprint import pprint


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, version):
        with open('token_vk.txt', 'r') as f:
            token = f.read().strip()
        self.params = {
            'access_token': token,
            'v': version
        }

        with open('token_ya.txt', 'r') as f:
            token_ya = f.read().strip()
        self.token_ya = token_ya

    def get_photos(self, pic_num, user_id=None):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'user_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'feed_type': 'photo',
            'photo_sizes': 1,
            'count': pic_num
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()

        items = res['response']['items']
        photos_links = []
        names = []
        sizes_list = []
        for pic_info in items:

            height_list = []

            for size in pic_info['sizes']:
                height_list.append(size['height'])

            for size in pic_info['sizes']:
                if size['height'] == max(height_list):  # succeeds always
                    photos_links.append(size['url'])
                    sizes_list.append(size['type'])
                    if str(pic_info['likes']['count']) not in names:
                        names.append(str(pic_info['likes']['count']))
                    else:
                        names.append(f"{str(pic_info['likes']['count'])}_{str(pic_info['date'])}")

        json_dict = []
        counter = 0

        while counter != pic_num:
            json_dict.append({})
            json_dict[counter]['file_name'] = f'{names[counter]}.jpg'
            json_dict[counter]['size'] = sizes_list[counter]

            counter += 1

        with open('info.json', 'w') as file:
            json.dump(json_dict, file)

        return photos_links

    def get_headers_yadisk(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def upload_to_yadisk(self):
        user_id = input('Input user_id:')




        disk_folder = input('Input yaDisk folder name:')
        photo_count = int(input('Input number of photos you want to save:'))
        upload_url = f'https://cloud-api.yandex.net/v1/disk/resources?path={disk_folder}'
        headers = self.get_headers_yadisk()
        response = requests.get(upload_url, headers=headers)
        res = response.json()

        if 'Resource not found.' in res.values():
            requests.put(upload_url, headers=headers)
        else:
            pass

        counter = 0
        for url in self.get_photos(pic_num=photo_count, user_id=user_id):

            upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = self.get_headers_yadisk()

            with open('info.json', 'r') as file:
                pic_info = json.load(file)

            params = {'path': f"{disk_folder}/{pic_info[counter]['file_name']}", 'overwrite': 'false', 'url': url}
            response = requests.post(upload_url, headers=headers, params=params)
            response.raise_for_status()

            print(f"{round((counter / photo_count) * 100)} % done")
            counter += 1
        print('100 % done - Success!')


if __name__ == "__main__":
    vk_client = VkUser('5.131')
    vk_client.upload_to_yadisk()