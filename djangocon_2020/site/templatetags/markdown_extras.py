from django import template
from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()


@register.filter()
@stringfilter
def markdown(value):
    f = open(value, 'r')
    f = f.read()
    return md.markdown(f, extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists'
        ])
