from flask import Flask, jsonify, render_template, request
from bs4 import BeautifulSoup
from urlparse import urljoin
import urllib2
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
    print('FIRST: ' + base_url)

    if(not base_url.startswith('http') and not base_url.startswith('www.')):
        base_url = 'http://www.' + base_url
    elif(not base_url.startswith('http')):
        base_url = 'http://' + base_url

    print('SECOND: ' + base_url)
    # Grab html from url requested
    req = urllib2.Request(base_url, headers={'User-Agent': 'Magic Browser'})
    html_doc = urllib2.urlopen(req)
    # Get beautiful soupped version of html doc
    soup = BeautifulSoup(html_doc, 'html.parser')
    urls = []
    local_urls = []

    # Grab all images > src tags and create full urls for them
    for img in soup.find_all('img'):
        if(img is not None):
            print(img.get('src'))
            img_src = img.get('src')
            if(img_src is not None):
                if(img_src.startswith('//')):
                    urls.append(img_src[2:])
                else:
                    joined_url = urljoin(base_url, img.get('src'))
                    urls.append(joined_url)
    
    # Download each image to server for serving to client
    local_directory = 'static/temp/' + str(int(round(time.time() * 1000))) + '/'
    for img_url in urls:
        try:
            full_url = img_url
            if(not img_url.startswith('http')):
                full_url = 'http://' + img_url

            extension = full_url[full_url.rfind('.'):]
            local_url = local_directory + str(urls.index(img_url)) + extension

            print('img_url -- ' + img_url)
            print('full url -- ' + full_url)
            print('local_url -- ' + local_url)

            if not os.path.exists(local_directory):
                os.makedirs(local_directory)

            f = open(local_url, 'w+')
            f.close()

            urllib.urlretrieve(full_url, local_url)
            local_urls.append(local_url)
        except Exception as e:
            print('failed to download ' + full_url)
            print('ERROR MSG -- ' + str(e.args))
    
    print('DONE GETTING URLS!\n' + str(local_urls))
    return jsonify(local_urls)

if __name__ == '__main__':
    app.run(port=3300, host='localhost')
