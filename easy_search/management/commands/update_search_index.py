from django.core.management.base import BaseCommand, CommandError
from easy_search.searcher import Searcher

class Command(BaseCommand):
    args = '<url_to_sitemap, url_to_sitemap, ... >'
    help = 'Recreate the search index from a given sitemap.xml file'

    def handle(self, *args, **options):
        s = Searcher()
        s.reset_index()
        for sitemap_url in  args:
            s.scan_site(sitemap_url)
