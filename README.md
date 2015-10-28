# django-easy-search


## Requirements

- Whoosh>=2.7
- beautifulsoup4>=4.4
- lxml>=3.5


## Installation

- Install the files.
- Add `easy_search` to your `INSTALLED_APPS`.
- Define an `INDEX_DIR` that defines where to put the files.
- Make sure the SITES module is enabled and the the default domain name is correct.
- Make sure you have a sitemap
- Create the search index  
  `python manage.py update_search_index <sitemap-url>`



## Changing the look

- Change the look of the search results by overriding the templates
  `easy_search/results.html`
  and
  `easy_search/_results.html`
