from django.core.management.base import BaseCommand, CommandError
from easy_search.searcher import Searcher

class Command(BaseCommand):
    args = '<url_to_sitemap, url_to_sitemap, ... >'
    help = 'Recreate the search index from a given sitemap.xml file'

    def add_arguments(self, parser):
        parser.add_argument('url', nargs='+', type=str)

    def handle(self, *args, **options):
        s = Searcher()
        s.reset_index()
        for sitemap_url in options['url']:
            s.scan_site(sitemap_url)
