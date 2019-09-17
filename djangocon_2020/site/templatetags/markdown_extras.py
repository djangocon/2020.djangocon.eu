from django import template
from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()


@register.filter()
@stringfilter
def markdown(value):
    r = {}
    f = open(value, 'r')
    f = f.read()
    m = md.Markdown(extensions = [
        'extra',
        'nl2br',
        'sane_lists',
        'meta'
        ])
    r['html'] = m.convert(f)
    r['meta'] = m.Meta
    return r
