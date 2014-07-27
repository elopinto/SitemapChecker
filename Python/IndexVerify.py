from sys import argv
from lxml import etree, html
from StringIO import StringIO
import requests
import csv
import os
import gzip

script, indexurl, savefolder = argv

# create folder to save files produced by running IndexVerify.py
os.mkdir(savefolder)

# Funtion: Get XML sitemap, parse with lxml, return list of URLs
def get_map(url):
    if url.endswith("gz"):
        compressed_sitemap = requests.get(url).content
        compressed_smstream = StringIO(compressed_sitemap)
        sitemap_page = gzip.GzipFile(fileobj=compressed_smstream)
        sitemap_page = sitemap_page.read()
        compressed_smstream.close()
    else:
        sitemap_page = requests.get(url).text
        sitemap_page = sitemap_page.encode('ascii', 'ignore')

    sitemap = etree.fromstring(sitemap_page)
    map_nodes = "{%s}loc" % sitemap.nsmap[None]
    sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]

    return sitemap_urls

# Function: Get webpage, parse HTML with lxml. Return canonical tag.
def check_canonical(request):
    source = request.text.encode('ascii', 'ignore')
    try:
        head = html.fromstring(source).head
        href = ''
        for item in head.iter('link'):
            if item.attrib['rel'] == 'canonical':
                href = item.attrib['href']
    except:
        href = 'Error parsing HTML'
    return href

# Function: Check status code and canonical tags of URLs in sitemap.
# Write results to CSV file.
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


# Get list of sitemaps in index.
index_urls = get_map(indexurl)

# Check status codes and canonical tags of URLs on each sitemap. Save
# results in CSV files in directory created at start of script.
for url in index_urls:
    saveas_filename = url.split("/")[-1] + ".csv"
    saveas_path = "%s\\%s" % (savefolder, saveas_filename)
    with open(saveas_path, 'wb') as target:
        filewriter = csv.writer(target, dialect='excel')
        filewriter.writerow([' ', 'URLs', 'Status Code',
                            'Canonical', 'Canonical Tag URL'])
        check_map(url)
