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


class EasySearchField(object):
    
    def __init__(self, soup, url):
        self.content = unicode(self.parse_soup(soup, url))


class TextField(EasySearchField):
    name = 'text'
    whoosh_field = TEXT(stored=True,spelling=True)
    
    def parse_soup(self, soup, url):
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text


class TitleField(EasySearchField):
    name = 'title'
    whoosh_field = TEXT(stored=True)
    
    def parse_soup(self, soup, url):
        return soup.title.string


class URLField(EasySearchField):
    name = 'url'
    whoosh_field = ID(stored=True)
    
    def parse_soup(self, soup, url):
        return url
        


DEFAULT_EASY_SEARCH_FIELDS = (
    URLField,
    TitleField,
    TextField,
)

EASY_SEARCH_FIELDS = getattr(
    settings,
    'EASY_SEARCH_FIELDS',
    DEFAULT_EASY_SEARCH_FIELDS
)



class Searcher:

    def __init__(self):
        self.find_search_fields()
        kwargs = self.get_schema_kwargs()
        self.schema = Schema(**kwargs)
        if not os.path.exists(settings.EASY_SEARCH_INDEX_DIR):
            os.mkdir(settings.EASY_SEARCH_INDEX_DIR)
            self.index = create_in(settings.EASY_SEARCH_INDEX_DIR,self.schema)
        self.index = open_dir(settings.EASY_SEARCH_INDEX_DIR)
    
    def find_search_fields(self):
        self.search_fields = EASY_SEARCH_FIELDS # TODO: Extend to class creation by string
    
    def get_schema_kwargs(self):
        return dict([
            (field.name, field.whoosh_field)
            for field in self.search_fields
        ])
    
    def reset_index(self):
        self.index = create_in(settings.EASY_SEARCH_INDEX_DIR,self.schema)

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
        soup = self.clean_soup(soup)
        
        document_kwargs = self.get_document_kwargs(soup, url)
        writer = self.index.writer()
        writer.add_document(**document_kwargs)
        writer.commit()
    
    def clean_soup(self, soup):
        for script in soup(["script", "style"]):
            script.extract() 
        for element in soup(['nav']):
            element.extract()
        for element in soup.findAll('div', {'class': 'no-search'}):
            element.extract()
        return soup
    
    def get_document_kwargs(self, soup, url):
        kwargs = {}
        for field in self.search_fields:
            key = field.name
            value = field(soup, url).content
            kwargs[key] = value
        return kwargs
    
    #do the search on the generated index.
    def search(self,query):
        if not query:
            return []
        search_result = []
        with self.index.searcher() as searcher:
            qp = QueryParser("text", schema=self.index.schema)
            q = qp.parse('*' + query + '*')
            results = searcher.search(q)
            results.fragmenter.surround = 20
            for r in results:
                res_obj = {'text': r.highlights("text"), 'url': r['url'], 'title': r['title'] }
                search_result.append(res_obj)
            return search_result

