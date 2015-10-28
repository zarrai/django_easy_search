from django.http import HttpResponse
from easy_search.searcher import Searcher
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView


class EasySearchResultsMixin(object):
    
    template_name = 'easy_search/results.html'
    
    def get_search_results(self, query):
        searcher = Searcher()
        results = searcher.search(query)
        return results
    
    def get_query(self):
        return self.request.GET.get('q', None)
    
    def get_context_data(self, **kwargs):
        context = super(EasySearchResultsMixin, self).get_context_data(**kwargs)
        query = self.get_query()
        object_list = self.get_search_results(query)
        context['query'] = query
        context['list'] = object_list
        return context


class EasySearchResultsView(EasySearchResultsMixin, TemplateView):
    pass
