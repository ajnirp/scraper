#!/usr/bin/env pypy3

import json
import urllib.request as url

CURR_COMIC_URI = 'http://xkcd.com/info.0.json'

def current():
    with url.urlopen(CURR_COMIC_URI) as response:
        contents = response.read()
        contents = ''.join(map(chr, contents))
        json_data = json.loads(contents)
        return json_data

def full_title(json_data):
    day = json_data['day']
    mon = int(json_data['month'])
    mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][mon]
    year = json_data['year']
    date = day + ' ' + mon + ' ' + year
    num = str(json_data['num'])
    title = json_data['title']
    full_title = num + ' - ' + title + ' (' + date + ')'
    return full_title

def save_comic(json_data, title='xkcd'):
    img_url = json_data['img']
    with url.urlopen(img_url) as response:
        contents = response.read()
        fname = title + '.png'
        with open(title, 'wb') as f:
            f.write(contents)

if __name__ == '__main__':
    json_data = current()
    title = full_title(json_data)
    save_comic(json_data, title)
    print('Alt text: ' + json_data['alt'])