from whoosh.fields import TEXT, ID
from whoosh.query import *


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
