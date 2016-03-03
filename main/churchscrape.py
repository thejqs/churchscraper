#!usr/bin/env python

'''
A small crawler project for a client that collects
PDF urls, names and files from across an entire website.
'''

import urllib
import urllib2
from lxml import etree
import StringIO
import re
import csv


class PDFScraper():
    @staticmethod
    def open_url(url):
        '''
        checks the url to make sure it's valid and, if so,
        reads in the html
        '''
        click = urllib.urlopen(url)
        if click.getcode() == 200:
            html = click.read()
            return html
        else:
            raise Exception("Nice try. Bad link.")

    @staticmethod
    def parse_html(html):
        '''
        the initial parse of the html
        '''
        parser = etree.HTMLParser()
        return etree.parse(StringIO.StringIO(html), parser)

    @staticmethod
    def treeify(url):
        '''
        gets the parsed tree to begin the scrape
        '''
        html = PDFScraper.open_url(url)
        return PDFScraper.parse_html(html)

    @staticmethod
    def get_locations(url):
        '''
        collects all the site urls to check for the files we want
        '''
        tree = PDFScraper.treeify(url)
        # locations = []
        return [location for location in tree.xpath('//*/urlset/url/loc/text()')]

    @staticmethod
    def find_files(locations):
        '''
        checks for the files and, if it finds one,
        notes its location in a csv and in a list
        '''
        pdf_urls = []

        for location in locations:
            tree = PDFScraper.treeify(location)

            try:
                pdf_url_xpath = '//*/a/@href'
                all_urls = tree.xpath(pdf_url_xpath)

                for one_url in all_urls:
                    if 'pdf' in one_url:
                        # the data we need to follow back to
                        # the original resources if need be
                        breadcrumbs = (location, one_url)
                        pdf_urls.append(breadcrumbs)
                        writer = csv.writer(open('new_pdf_urls.csv', 'a'))
                        writer.writerow(breadcrumbs)

            # many urls won't contain pdf links
            # we really don't care about those or the error type;
            # in this case we just need to keep going.
            # terminal output is enough to check a few manually
            # to verify we're not missing anything
            except:
                print location
                continue

    @staticmethod
    def collect_files(pdf_urls):
        '''
        pulls down all the pdfs, constructing new file names
        from the url structure to make them easy to match later
        '''
        for url in pdf_urls:
            web_file = urllib.urlopen(pdf)

            # these will need names when we save them; stealing those from
            # the url structure to make them easier to trace back.
            # even doing this loosely is plenty helpful in this case
            pdf_name_pattern = '(\w+(?=\.pdf))'
            name_match = re.search(pdf_name_pattern, '{0}'.format(url))
            name_final = name_match.group()
            # print name_match

            with open('mcmillan_pdfs/{0}.pdf'.format(name_final), 'a+') as f:
                f.write(web_file.read())

    @staticmethod
    def start_scrape():
        '''
        starts the whole ball o' wax
        '''
        # the site has helpfully provided xml of its urls;
        # if it hadn't, could have generated this a different way
        locations = PDFScraper.get_locations('http://www.johnmcmillanpc.org/site_map_xml.php')
        pdf_urls = PDFScraper.find_files(locations)
        PDFScraper.collect_files(pdf_urls)
