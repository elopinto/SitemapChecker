from sys import argv, platform
from lxml import etree, html
from threading import Thread
import requests
import csv
import os


script, sitemapurl, saveas = argv

# open online xml sitemap file, create object with etree, and get namespace
sitemap_page = requests.get(sitemapurl).text
sitemap_page = sitemap_page.encode('utf_8', 'ignore')
sitemap = etree.fromstring(sitemap_page)
map_nodes = "{%s}loc" % sitemap.nsmap[None]

# make list of webpage URLs from sitemap
sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]

# detect os and set directory for temporary files
if platform == 'win32':
    tempdir = os.getenv('TEMP') + '\\'
else:
    tempdir = '/tmp/'

tempfiles = []

# Check if page on sitemap has canonical tag and if the tag points to the
# page URL
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

# Make web request for each URL in specified range of sitemap. If URL returns a
# 200 status code, check for canonical tags. Write results to temporary CSV.
def check_map(start, stop, chunknum):
    saveas_filename = "%ssm_check_temp%d.csv" % (tempdir, chunknum)
    tempfiles.append(saveas_filename)
    with open(saveas_filename, 'wb') as target:
        filewriter = csv.writer(target, dialect='excel')
        for url in sitemap_urls[start:stop]:
            r = requests.get(url, allow_redirects=False)
            status_code = r.status_code
            if status_code == 200:
                canonical_url = check_canonical(r)
            else:
                canonical_url = ''	
            iscanonical = canonical_url == url
            filewriter.writerow([url, status_code,
                                iscanonical, canonical_url])
            print url, status_code, iscanonical

# Copy data from temporary CSV to final CSV. Return number of rows in final CSV.
def combine(final_writer, input_file, num):
    with open(input_file, 'rb') as source:
        item_source = csv.reader(source, dialect='excel')
        item = num
        for row in item_source:
            row.insert(0, num)
            final_writer.writerow(row)
            num += 1
    return num


# Get number of URLs in sitemap and divide by 10 to decide how many URLs each
# thread should check.
number_of_items = len(sitemap_urls)
chunk = number_of_items / 10

# Create 10 threads, each checking a different tenth or the sitemap
ta = Thread(target=check_map, args=(0, chunk, 1))
tb = Thread(target=check_map, args=(chunk, chunk*2, 2))
tc = Thread(target=check_map, args=(chunk*2, chunk*3, 3))
td = Thread(target=check_map, args=(chunk*3, chunk*4, 4))
te = Thread(target=check_map, args=(chunk*4, chunk*5, 5))
tf = Thread(target=check_map, args=(chunk*5, chunk*6, 6))
tg = Thread(target=check_map, args=(chunk*6, chunk*7, 7))
th = Thread(target=check_map, args=(chunk*7, chunk*8, 8))
ti = Thread(target=check_map, args=(chunk*8, chunk*9, 9))
tj = Thread(target=check_map, args=(chunk*9, chunk*10+1, 10))

threads = [ta, tb, tc, td, te, tf, tg, th, ti, tj]

# Start checking sitemap, wait for all threads to finish before continuing
for thread in threads:
    thread.start()
    
for thread in threads:
    thread.join()

# Combine results from each thread in final CSV document
with open(saveas, 'wb') as final_target:
    final_writer = csv.writer(final_target, dialect='excel')
    final_writer.writerow([' ', 'URLs', 'Status Code',
                            'Canonical', 'Canonical Tag URL'])
    num = 1
    for file in tempfiles:
        num = combine(final_writer, file, num)

# Delete temporary CSV files
for file in tempfiles:
    os.remove(file)
