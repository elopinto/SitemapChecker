from sys import argv
from lxml import etree, html
import requests
import csv

script, indexurl, map_number = argv


def get_map(url):
    sitemap_page = requests.get(url).text
    sitemap_page = sitemap_page.encode('ascii', 'ignore')
    sitemap = etree.fromstring(sitemap_page)
    map_nodes = "{%s}loc" % sitemap.nsmap[None]
    sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]
    return sitemap_urls

def check_canonical(request):
    source = request.text.encode('ascii', 'ignore')
    head = html.fromstring(source).head
    href = ''
    for item in head.iter('link'):
        if item.attrib['rel'] == 'canonical':
            href = item.attrib['href']
        else:
            pass
    return href
	
def check_map(url):
    sitemap_urls = get_map(url)
    item = 1
    for url in sitemap_urls:
        r = requests.get(url, allow_redirects=False)
        status_code = r.status_code
        if status_code == 200:
            canonical_url = check_canonical(r)
        else:
            canonical_url = ''	
        iscanonical = canonical_url == url
        filewriter.writerow([item, url, status_code,
                            iscanonical, canonical_url])
        print "\n%d / %d :" % (item, len(sitemap_urls))
        print url, status_code, iscanonical
        item += 1


index_urls = get_map(indexurl)

for url in index_urls[map_number:]:
    saveas_filename = url.split("/")[-1] + ".csv"
    target = open(saveas_filename, 'wb')
    filewriter = csv.writer(target, dialect='excel')
    filewriter.writerow([' ', 'URLs', 'Status Code',
                        'Canonical', 'Canonical Tag URL'])
    check_map(url)
    target.close()
