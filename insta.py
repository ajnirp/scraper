#!/usr/bin/env python3
# instagram scraper

import re
import sys
import urllib.request as u

USAGE = 'usage: insta.py <url>'
IMG_REGEX = '<meta property="og:image" content="(.+?)" ?/>'

# download an instagram pic
def download(insta_url):
    fname = insta_url.split('/')[-1]
    with u.urlopen(insta_url) as response:
        contents = response.read()
        with open(fname, 'wb') as f:
            f.write(contents)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    with u.urlopen(url) as response:
        html_source = str(response.read())
        imgs = re.findall(IMG_REGEX, html_source)
        if imgs == []:
            print('no images found :(', file=sys.stderr)
            sys.exit(1)
        download(imgs[0])