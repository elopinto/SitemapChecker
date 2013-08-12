from sys import argv
from lxml import etree, html
import requests
import csv


script, sitemapurl, saveas = argv


sitemap_page = requests.get(sitemapurl).text
sitemap_page = sitemap_page.encode('utf_8', 'ignore')
sitemap = etree.fromstring(sitemap_page)
map_nodes = "{%s}loc" % sitemap.nsmap[None]


def check_canonical(request):
    source = request.text.encode('utf_8', 'ignore')
    head = html.fromstring(source).head
    href = ''
    for item in head.iter('link'):
        if item.attrib['rel'] == 'canonical':
            href = item.attrib['href']
        else:
            pass
    return href


sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]

with open(saveas, 'wb') as target:
    filewriter = csv.writer(target, dialect='excel')
    filewriter.writerow([' ', 'URLs', 'Status Code',
                        'Canonical', 'Canonical Tag URL'])
    num = 1
    for url in sitemap_urls:
        r = requests.get(url, allow_redirects=False)
        status_code = r.status_code
        if status_code == 200:
            canonical_url = check_canonical(r)
        else:
            canonical_url = ''	
        iscanonical = canonical_url == url
        filewriter.writerow([num, url, status_code, iscanonical, canonical_url])
        print "\n%d / %d :" % (num, len(sitemap_urls))
        print url, status_code, iscanonical
        num += 1
        