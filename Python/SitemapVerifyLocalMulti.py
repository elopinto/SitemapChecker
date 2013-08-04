from sys import argv
from lxml import etree, html
from threading import Thread
import requests
import csv
import os


script, sitemapfile, saveas = argv


sitemap_page = open(sitemapfile).read()
sitemap = etree.fromstring(sitemap_page)
map_nodes = "{%s}loc" % sitemap.nsmap[None]

sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]


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
    
def check_map(start, stop, chunknum):
    saveas_filename = "sm_check_temp%d.csv" % chunknum
    target = open(saveas_filename, 'wb')
    filewriter = csv.writer(target, dialect='excel')
    filewriter.writerow([' ', 'URLs', 'Status Code',
                        'Canonical', 'Canonical Tag URL'])
    item = 1
    for url in sitemap_urls[start:stop]:
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
    target.clost()


number_of_items = len(sitemap_urls)
chunk = number_of_items / 10

Thread(target=check_map, args=(0, chunk, 1)).start()
Thread(target=check_map, args=(chunk, chunk*2, 2)).start()
Thread(target=check_map, args=(chunk*2, chunk*3, 3)).start()
Thread(target=check_map, args=(chunk*3, chunk*4, 4)).start()
Thread(target=check_map, args=(chunk*4, chunk*5, 5)).start()
Thread(target=check_map, args=(chunk*5, chunk*6, 6)).start()
Thread(target=check_map, args=(chunk*6, chunk*7, 7)).start()
Thread(target=check_map, args=(chunk*7, chunk*8, 8)).start()
Thread(target=check_map, args=(chunk*8, chunk*9, 9)).start()
Thread(target=check_map, args=(chunk*9, chunk*10, 10)).start()

tempfiles = [
    "sm_check_temp1.csv", "sm_check_temp2.csv", "sm_check_temp3.csv",
    "sm_check_temp4.csv", "sm_check_temp5.csv", "sm_check_temp6.csv",
    "sm_check_temp7.csv", "sm_check_temp8.csv", "sm_check_temp9.csv",
    "sm_check_temp10.csv"
    ]

with open(saveas, 'wb') as final_target:
    final_writer = csv.writer(final_target, dialect='excel')
    for file in tempfiles:
        with open(file, 'rb') as source:
            item_source = csv.reader(source, dialect='excel')
            for row in item_source:
                final_writer.writerow(row)

for file in tempfiles:
    os.remove(file)
