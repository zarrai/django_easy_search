from django.http import HttpResponse
from easy_search.simple_site_searcher import SimpleSiteSearcher
from django.shortcuts import render_to_response
from django.template import RequestContext

def results(request):
    query = request.GET.get('q', None)
    searcher = SimpleSiteSearcher()
    results = searcher.search(query)
    return render_to_response(
        'easy_search/results.html',
        {'list': results, 'query': query},
        context_instance=RequestContext(request)
    )
