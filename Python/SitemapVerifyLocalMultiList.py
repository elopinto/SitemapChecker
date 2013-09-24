from sys import argv
from lxml import etree, html
from threading import Thread
import requests
import csv


script, sitemapfile, saveas = argv

# open local xml sitemap file, create object with etree, and get namespaces
sitemap_page = open(sitemapfile).read()
sitemap = etree.fromstring(sitemap_page)
map_nodes = "{%s}loc" % sitemap.nsmap[None]

# make list of URLs from sitemap
sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]

tempfiles = {}

# Function: Check if page on sitemap has canonical tag and if the tag points to
# the page URL
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

# Function: Make web request for each URL in specified range of sitemap. If URL
# returns a 200 status code, check for canonical tags. Add results to
# temporary dictionary.
def check_map(start, stop, chunknum):
    results = []
    for url in sitemap_urls[start:stop]:
        r = requests.get(url, allow_redirects=False)
        status_code = r.status_code
        if status_code == 200:
            canonical_url = check_canonical(r)
        else:
            canonical_url = ''	
        iscanonical = canonical_url == url
        results.append([url, status_code, iscanonical, canonical_url])
        print url, status_code, iscanonical
    tempfiles['chunk%d' % chunknum] = results

# Function: Copy data from temporary dictionary to final CSV. Return number of
# rows in final CSV.
def combine(final_writer, input_list, num):
    for row in input_list:
        row.insert(0, num)
        final_writer.writerow(row)
        num += 1
    return num


# Get number of URLs in sitemap and divide by 10 to decide how many URLs each
# thread should check.
number_of_items = len(sitemap_urls)
chunk = number_of_items / 10
remainder = number_of_items - chunk * 10

# Create 10 threads, each checking a different tenth of the sitemap
ta = Thread(target=check_map, args=(0, chunk, 0))
tb = Thread(target=check_map, args=(chunk, chunk*2, 1))
tc = Thread(target=check_map, args=(chunk*2, chunk*3, 2))
td = Thread(target=check_map, args=(chunk*3, chunk*4, 3))
te = Thread(target=check_map, args=(chunk*4, chunk*5, 4))
tf = Thread(target=check_map, args=(chunk*5, chunk*6, 5))
tg = Thread(target=check_map, args=(chunk*6, chunk*7, 6))
th = Thread(target=check_map, args=(chunk*7, chunk*8, 7))
ti = Thread(target=check_map, args=(chunk*8, chunk*9, 8))
tj = Thread(target=check_map, args=(chunk*9, chunk*10+remainder, 9))

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
    sorted_temps = sorted(tempfiles.keys())
    num = 1
    for tlist in sorted_temps:
        num = combine(final_writer, tempfiles[tlist], num)
