from django.conf.urls import *  # NOQA

from .views import EasySearchResultsView


urlpatterns = patterns('',
    url(r'^$', EasySearchResultsView.as_view(), name='search-results')
)
