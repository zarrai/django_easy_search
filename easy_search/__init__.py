import urllib
from bs4 import BeautifulSoup
import os.path
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser
from lxml import etree
from StringIO import StringIO
from django.conf import settings

class SimpleSiteSearcher:

    def __init__(self):
        self.schema = Schema(url=ID(stored=True), text=TEXT(stored=True,spelling=True), title=TEXT(stored=True))
        if not os.path.exists(settings.INDEX_DIR):
            os.mkdir(settings.INDEX_DIR)
            self.index = create_in(settings.INDEX_DIR,self.schema)
        self.index = open_dir(settings.INDEX_DIR)


    def reset_index(self):
        self.index = create_in("index",self.schema)

    #scan a site based on a sitemap url
    def scan_site(self,sitemap_url):
        sitemap =  urllib.urlopen(sitemap_url).read()
        urls = etree.iterparse(StringIO(sitemap), tag='{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        NS = {
            'x': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'x2': 'http://www.google.com/schemas/sitemap-mobile/1.0'
        }

        for event, url in urls:
            search_url = url.xpath('.//x:loc/text()', namespaces=NS)[0]
            self._parse_url(unicode(search_url))


    def _parse_url(self,url):
        print "scanning url: %s" % url
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        writer = self.index.writer()
        print "url %s text %s" % (url,text)
        title = soup.title.string
        writer.add_document(url=unicode(url), text=unicode(text), title=unicode(title))
        writer.commit()

    #do the search on the generated index.
    def search(self,query):
        search_result = []
        with self.index.searcher() as searcher:
            qp = QueryParser("text", schema=self.index.schema)
            q = qp.parse('*' + query + '*')
            results = searcher.search(q)
            results.fragmenter.surround = 20
            for r in results:
                res_obj = {'text': r.highlights("text"), 'url': r['url'], 'title': r['title'] }
                search_result.append(res_obj)
            print search_result
            return search_result

