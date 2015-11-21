from django.http import HttpResponse
from easy_search.searcher import Searcher
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView


class EasySearchResultsMixin(object):
    
    template_name = 'easy_search/results.html'
    
    def get_query(self):
        return self.request.GET.get('q', '')
    
    def get_context_data(self, **kwargs):
        context = super(EasySearchResultsMixin, self).get_context_data(**kwargs)
        query = self.get_query()
        object_list = self.get_search_results(query)
        context['easy_search_string'] = query
        context['easy_search_results'] = object_list
        return context

    def get_search_results(self, query):
        self._search_results = []
        if query:
            self.search(query)
        return self._search_results

    def search(self, query):
        easy_searcher = Searcher()
        query = '*%s*' % query
        with easy_searcher.index.searcher() as searcher:
            q = easy_searcher.get_whoosh_query(query)
            results = searcher.search(q)
            results.fragmenter.surround = 20
            for r in results:
                res_obj = easy_searcher.get_result_dict(r)
                self._search_results.append(res_obj)


class EasySearchResultsView(EasySearchResultsMixin, TemplateView):
    pass
