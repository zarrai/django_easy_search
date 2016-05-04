# django-easy-search


This module should help to get started with a proper full text search.


## Requirements

- Whoosh>=2.7
- beautifulsoup4>=4.4
- lxml>=3.5


## Installation

- Install the files.
- Add `easy_search` to your `INSTALLED_APPS`.
- Include the necessary urls:  
  `url(r'^search/', include('easy_search.urls'))`
- Define an `EASY_SEARCH_INDEX_DIR` in your settings file where to put the search index files.
- Make sure the SITES module is enabled and the default domain name is correct.
- Make sure you have a sitemap
- Create the search index  
  `python manage.py update_search_index <sitemap-url>`



## Changing the look

- Change the look of the search results by overriding the templates
  `easy_search/results.html`
  and
  `easy_search/_results.html`


## Changing the view

If you would like to e.g. add additional template variables or change
the template file, you can override the view.
Do this by inheriting from `easy_search.views.EasySearchResultsMixin`.


## Template Tags

To display the search form, you can use the `get_search_form` template
tag. Load the template library `search_form` and don't forget to use
the GET method when displaying the form.
