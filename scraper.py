#!/usr/bin/env python

'''
multithreaded scraper that can download:
1. all tistory CDN images from a URL
2. all images in a given file (use --file)
'''

import urllib2, re, threading
from sys import argv
from subprocess import call
from os.path import isfile

NUM_THREADS = 4

class Downloader(threading.Thread):
    def __init__(self, url, thread_id, urls, num_threads):
        self.url = url
        self.urls = urls
        self.thread_id = thread_id
        self.num_threads = num_threads
        threading.Thread.__init__(self)

    def run(self):
        for idx, pair in enumerate(self.urls):
            image, num = pair
            num += 1
            filename = form_filename(url, num)
            grab_pic(image, filename, self.thread_id)

def file_exists(filename):
    '''check if a file already exists. i preprend some files with an
underscore or a hyphen for easier identification, so this function
checks both possibilities'''
    return isfile(filename) or isfile('_' + filename)

def grab_pic(url, filename, thread_id):
    '''use urllib2 to download a file'''
    if file_exists(filename):
        print filename + ' already exists'
    else:
        with open(filename, 'wb') as f:
            contents = urllib2.urlopen(url)
            f.write(contents.read())
            print 'thread ' + str(1 + thread_id) + ' => wrote ' + filename

def divide_tasks(urls, num_threads=NUM_THREADS):
    per_thread = len(urls) / num_threads
    groups = [[] for i in xrange(num_threads)]

    first_set = per_thread*num_threads
    for idx in xrange(first_set):
        groups[idx / per_thread].append((urls[idx], idx))

    remainder_set = len(urls) - first_set
    for i in xrange(remainder_set):
        idx = first_set + i
        groups[i].append((urls[idx], idx))

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

def grab_pics(url, images):
    if len(images) == 0:
        print 'Nothing to download'
        return

    print len(images), 'images in total'

    if len(images) < NUM_THREADS:
        for thread_id, image in enumerate(images):
            Downloader(url, thread_id, [(image, thread_id)], NUM_THREADS).start()
    else:
        groups = divide_tasks(images, NUM_THREADS)
        for thread_id, group in enumerate(groups):
            Downloader(url, thread_id, group, NUM_THREADS).start()

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

    grab_pics(url, pics)
