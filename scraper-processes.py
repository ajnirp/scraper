#!/usr/bin/env python

'''
multithreaded scraper that can download:
1. all tistory CDN images from a URL
2. all images in a given file (use --file)
'''

import urllib2, re
from sys import argv
from subprocess import call
from os.path import isfile
from multiprocessing import Pool

NUM_PROCESSES = 4

def file_exists(filename):
    '''check if a file already exists. i preprend some files with an
underscore or a hyphen for easier identification, so this function
checks both possibilities'''
    return isfile(filename) or isfile('_' + filename)

    return groups

def form_filename(url, idx):
    return tistory_id(url) + str(idx) + '.jpg'

def find_pics(url):
    print 'Fetching page source for', url
    response = urllib2.urlopen(url)
    page_source = response.read()

    original_regex = "http:\/\/cfile\d\d?\.uf\.tistory\.com\/original\/[A-Z0-9]+"
    image_regex = "http:\/\/cfile\d\d?\.uf\.tistory\.com\/image\/[A-Z0-9]+"

    images = re.findall(image_regex, page_source)
    originals = re.findall(original_regex, page_source)

    images = originals + [image.replace('image', 'original') for image in images]
    images = list(set(images))

    return images

def grab_pic(pair):
    idx, url = pair
    filename = form_filename('', 1+idx)
    proc_id = idx % 4
    with open(filename, 'wb') as f:
        contents = urllib2.urlopen(url)
        f.write(contents.read())
        print 'process ' + str(1 + proc_id) + ' => wrote ' + filename

def sanitise(url):
    '''prepend 'http' to the url in case it isn't already there'''
    return 'http://' + url if not url.startswith('http') else url

def tistory_id(url):
    '''if URL is a tistory url, extract the tistory name and append
the page number'''
    result = ''

    if 'tistory' in url:
        url_split = url.split('/')
        tistory_name = url_split[2]
        tistory_name = tistory_name.split('.')[0]
        page_number = url_split[-1]
        result = tistory_name + '-' + page_number + '-'

    return result

if __name__ == '__main__':
    pics = []
    url = ''

    if argv[1] == '--file':
        filename = argv[2]
        with open(filename, 'r') as f:
            pics = f.readlines()

    elif argv[1] == '--url':
        url = argv[2]
        url = sanitise(url)
        pics = [url]

    else:
        url = argv[1]
        url = sanitise(url)
        pics = find_pics(url)

    p = Pool(4)
    p.map(grab_pic, enumerate(pics))
