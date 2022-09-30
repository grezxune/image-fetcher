from flask import Flask, jsonify, render_template, request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import http.client as httplib
import urllib
import time
import os

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch-images', methods=['PUT'])
def fetch_images():
    base_url = request.json['base_url']
    # Prepend base_url with http:// or http://www. if missing from user
    base_url = decorate_url_with_protocol(base_url)

    print(base_url)
    # Get full urls & if hotlinking is possible or not
    urls_and_hotlink = get_image_urls(base_url)
    urls = urls_and_hotlink['urls']
    hotlink = urls_and_hotlink['hotlink']
    
    # Download images if necessary, compile list of urls to return. Local or remote
    final_urls = get_final_urls(urls, hotlink)
    
    print('DONE GETTING URLS!\n' + str(final_urls))
    return jsonify(final_urls)


def decorate_url_with_protocol(url):
    if(not url.startswith('http') and not url.startswith('www.')):
        # Pretty large assumption here - but will work for *most* cases
        url = 'http://www.' + url
    elif(not url.startswith('http')):
        # Another pretty large assumption here - but will work for *most* cases
        url = 'http://' + url

    return url


def get_image_urls(url):
    # Declare these for later consumption
    html_doc = None
    soup = None
    hotlink = True

    # Grab html from url - Headers set to avoid hotlink protection
    try:
        req = urllib.request.Request(url)
        html_doc = urllib.request.urlopen(req)
    except:
        req = urllib.request.Request(url, headers={'User-Agent': 'Magic Browser'})
        html_doc = urllib.request.urlopen(req)
        hotlink = False


    # Get beautiful soupped version of html doc
    soup = BeautifulSoup(html_doc, 'html.parser')

    urls = []

    # Grab all images > src tags and create full urls for them
    for img in soup.find_all('img'):
        if(img is not None):
            img_src = img.get('src')
            print(img_src)
            if(img_src is not None):
                if(img_src.startswith('//')):
                    urls.append(img_src[2:])
                else:
                    joined_url = urljoin(url, img.get('src'))
                    urls.append(joined_url)

    return {'urls': urls, 'hotlink': hotlink}


def get_final_urls(urls, hotlink):
    final_urls = []
    local_directory = 'static/temp/' + str(int(round(time.time() * 1000))) + '/'

    for img_url in urls:
        try:
            full_url = img_url
            if(not img_url.startswith('http')):
                full_url = 'http://' + img_url

            extension = full_url[full_url.rfind('.'):]
            local_url = local_directory + str(urls.index(img_url)) + extension

            if not os.path.exists(local_directory):
                os.makedirs(local_directory)

            if(hotlink):
                try:
                    img_req = urllib.request.Request(full_url)
                    urllib.request.urlopen(img_req)
                    final_urls.append(full_url)
                except:
                    urllib.request.urlretrieve(full_url, local_url)
                    final_urls.append(local_url)
            else:
                urllib.request.urlretrieve(full_url, local_url)
                final_urls.append(local_url)
        except Exception as e:
            print('failed to download ' + full_url)
            print('ERROR MSG -- ' + str(e.args))

    return final_urls


if __name__ == '__main__':
    app.run(port=3300, host='localhost')
