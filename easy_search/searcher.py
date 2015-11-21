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


class EasySearchField(object):
    
    def __init__(self, soup, url):
        self.content = unicode(self.parse_soup(soup, url))
    
    @classmethod
    def get_display(cls, result):
        return result.get(cls.name, '')


class TextField(EasySearchField):
    name = 'text'
    whoosh_field = TEXT(stored=True,spelling=True)
    
    def parse_soup(self, soup, url):
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    
    @classmethod
    def get_display(cls, result):
        return result.highlights("text")


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


class LanguageField(EasySearchField):
    name = 'language'
    whoosh_field = TEXT(stored=True)
    
    def parse_soup(self, soup, url):
        return soup.html.attrs.get('lang', '')


class OgImageField(EasySearchField):
    name = 'og_image'
    whoosh_field = TEXT(stored=True)
    
    def parse_soup(self, soup, url):
        image = soup.find('meta', attrs={'property': 'og:image'}) or {}
        return image.get('content', '')


class MetaDescriptionField(EasySearchField):
    name = 'description'
    whoosh_field = TEXT(stored=True)
    
    def parse_soup(self, soup, url):
        description = soup.find('meta', attrs={'name': 'description'}) or {}
        return description.get('content', '')


DEFAULT_EASY_SEARCH_FIELDS = [
    URLField,
    TitleField,
    TextField,
    LanguageField,
    OgImageField,
    MetaDescriptionField,
]

EASY_SEARCH_FIELDS = getattr(
    settings,
    'EASY_SEARCH_FIELDS',
    DEFAULT_EASY_SEARCH_FIELDS
)

EASY_SEARCH_FIELDS = EASY_SEARCH_FIELDS + getattr(
    settings,
    'ADD_EASY_SEARCH_FIELDS',
    []
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
                
        
