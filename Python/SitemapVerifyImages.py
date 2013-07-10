from sys import argv
from lxml import etree, html
import requests
import csv


script, sitemapurl, saveas = argv
target = open(saveas, 'wb')
filewriter = csv.writer(target, dialect='excel')

sitemap_page = requests.get(sitemapurl).text
sitemap_page = sitemap_page.encode('ascii', 'ignore')
sitemap = etree.fromstring(sitemap_page)
map_nodes = "{%s}loc" % sitemap.nsmap["image"]


# def check_canonical(request):
    # source = request.text.encode('ascii', 'ignore')
    # head = html.fromstring(source).head
    # href = ''
    # for item in head.iter('link'):
        # if item.attrib['rel'] == 'canonical':
            # href = item.attrib['href']
        # else:
            # pass
    # return href


sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]

filewriter.writerow([' ', 'URLs', 'Status Code'])

num = 1
for url in sitemap_urls:
    r = requests.get(url, allow_redirects=False)
    status_code = r.status_code
    filewriter.writerow([num, url, status_code])
    print "\n%d / %d :" % (num, len(sitemap_urls))
    print url, status_code
    num += 1

target.close()
