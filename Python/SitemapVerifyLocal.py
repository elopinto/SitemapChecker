from sys import argv
from lxml import etree, html
import requests
import csv


script, sitemapfile, saveas = argv


# Open locally saved XML sitemap, parse with lxml. Get default namespace.
sitemap_page = open(sitemapfile).read()
sitemap = etree.fromstring(sitemap_page)
map_nodes = "{%s}loc" % sitemap.nsmap[None]


# Function: Get page listed on sitemap. Return canonical tag.
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


# Make list of URLs from sitemap.
sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]

# Check status codes and canonical tags of each URL, save results to CSV file.
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
