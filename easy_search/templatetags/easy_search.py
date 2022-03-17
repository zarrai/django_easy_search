from django.utils.translation import ugettext_lazy as _
from django import forms
from django import template


register = template.Library()


class SearchForm(forms.Form):
    q = forms.CharField(
        label=_('Search'),
        widget=forms.TextInput(attrs={'placeholder':_('Search')})
    )


@register.simple_tag(takes_context=True)
def get_search_form(context):
    value = context['request'].GET.get('q', '')
    return SearchForm(initial={'q': value})
