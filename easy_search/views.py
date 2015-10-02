from django.http import HttpResponse
from easy_search.searcher import Searcher
from django.shortcuts import render_to_response
from django.template import RequestContext

def results(request):
    query = request.GET.get('q', None)
    searcher = Searcher()
    results = searcher.search(query)
    return render_to_response(
        'easy_search/results.html',
        {'list': results, 'query': query},
        context_instance=RequestContext(request)
    )
