from sys import argv
from lxml import etree, html
from threading import Thread
import requests
import csv
import os

script, indexurl, savefolder = argv

os.mkdir(savefolder)

class MapChecker(object):

    def __init__(self, url):
        self.tempfiles = {}
        self.sitemap_urls = self.get_map(url)

    def get_map(self, url):
        sitemap_page = requests.get(url).text
        sitemap_page = sitemap_page.encode('utf_8', 'ignore')
        sitemap = etree.fromstring(sitemap_page)
        map_nodes = "{%s}loc" % sitemap.nsmap[None]
        sitemap_urls = [url.text.strip() for url in sitemap.iter(map_nodes)]
        return sitemap_urls

    def check_canonical(self, request):
        source = request.text.encode('utf_8', 'ignore')
        head = html.fromstring(source).head
        href = ''
        for item in head.iter('link'):
            if item.attrib['rel'] == 'canonical':
                href = item.attrib['href']
            else:
                pass
        return href
	
    def check_section(self, start, stop, chunknum):
        results = []
        for url in self.sitemap_urls[start:stop]:
            r = requests.get(url, allow_redirects=False)
            status_code = r.status_code
            if status_code == 200:
                canonical_url = self.check_canonical(r)
            else:
                canonical_url = ''	
            iscanonical = canonical_url == url
            results.append([url, status_code, iscanonical, canonical_url])
            print url, status_code, iscanonical
        self.tempfiles['chunk%d' % chunknum] = results

    def combine(self, final_writer, input_list, num):
        item = num
        for row in input_list:
            row.insert(0, num)
            final_writer.writerow(row)
            num += 1
        return num
    
    def check_map(self):
        number_of_items = len(self.sitemap_urls)
        chunk = number_of_items / 10
        remainder = number_of_items - chunk * 10
        ta = Thread(target=self.check_section, args=(0, chunk, 0))
        tb = Thread(target=self.check_section, args=(chunk, chunk*2, 1))
        tc = Thread(target=self.check_section, args=(chunk*2, chunk*3, 2))
        td = Thread(target=self.check_section, args=(chunk*3, chunk*4, 3))
        te = Thread(target=self.check_section, args=(chunk*4, chunk*5, 4))
        tf = Thread(target=self.check_section, args=(chunk*5, chunk*6, 5))
        tg = Thread(target=self.check_section, args=(chunk*6, chunk*7, 6))
        th = Thread(target=self.check_section, args=(chunk*7, chunk*8, 7))
        ti = Thread(target=self.check_section, args=(chunk*8, chunk*9, 8))
        tj = Thread(target=self.check_section, args=(chunk*9, chunk*10+remainder, 9))

        threads = [ta, tb, tc, td, te, tf, tg, th, ti, tj]

        for thread in threads:
            thread.start()
    
        for thread in threads:
            thread.join()
            
    def write_results(self, saveas):
        with open(saveas, 'wb') as final_target:
            final_writer = csv.writer(final_target, dialect='excel')
            final_writer.writerow([' ', 'URLs', 'Status Code',
                                'Canonical', 'Canonical Tag URL'])
            sorted_temps = sorted(self.tempfiles.keys())
            num = 1
            for tlist in sorted_temps:
                num = self.combine(final_writer, self.tempfiles[tlist], num)


class IndexChecker(object):

    def __init__(self, index_urls):
        self.index_urls = index_urls
        
    def check_section(self, start, stop):
        for url in self.index_urls[start:stop]:
            saveas_filename = url.split("/")[-1] + ".csv"
            saveas_path = "%s\\%s" % (savefolder, saveas_filename)
            map_scanner = MapChecker(url)
            map_scanner.check_map()
            map_scanner.write_results(saveas_path)
        
    def check_index(self):
        number_of_items = len(self.index_urls)
        chunk = number_of_items / 3
        remainder = number_of_items - chunk * 3
        pa = Thread(target=self.check_section, args=(0, chunk))
        pb = Thread(target=self.check_section, args=(chunk, chunk*2))
        pc = Thread(target=self.check_section, args=(chunk*2, chunk*3+remainder))
        threads = [pa, pb, pc]
        
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()


index_scanner = MapChecker(indexurl)

index_processor = IndexChecker(index_scanner.sitemap_urls)

index_processor.check_index()
