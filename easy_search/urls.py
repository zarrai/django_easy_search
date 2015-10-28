from django.conf.urls import *  # NOQA

urlpatterns = patterns('',
    url(r'^$', 'easy_search.views.results')
)
