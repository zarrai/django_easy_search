import importlib
import urllib
from bs4 import BeautifulSoup
import os.path
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser

from lxml import etree
from StringIO import StringIO
from django.conf import settings




DEFAULT_EASY_SEARCH_FIELDS = (
    'easy_search.fields.URLField',
    'easy_search.fields.TitleField',
    'easy_search.fields.TextField',
    'easy_search.fields.LanguageField',
    'easy_search.fields.OgImageField',
    'easy_search.fields.MetaDescriptionField',
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
        self.search_fields = []
        for field in EASY_SEARCH_FIELDS:
            module_name, class_name = field.rsplit('.', 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            self.search_fields.append(cls)
    
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

    def get_field_names(self):
        return [f.name for f in self.search_fields]
    
    def get_result_dict(self, result):
        return dict([
            (f.name, f.get_display(result))
            for f in self.search_fields
        ])
    
    def get_whoosh_query(self, string):
        query = None
        for field in self.search_fields:
            if query is None:
                query = Wildcard(field.name, string)
            else:
                query = query | Wildcard(field.name, string)
        return query
                
        
