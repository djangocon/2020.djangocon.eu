import markdown
from django.shortcuts import render
from os import walk

from config.settings.base import APPS_DIR

def default_view(request, menu='home', submenu=None):
    sub_path = menu + ('/' + submenu if submenu else '')
    path = APPS_DIR.__str__() + '/content/' + sub_path + '/'
    ctx = {}
    files = []
    for dirpath, dirname, filenames in walk(path):
        files.extend(filenames)
        break
    for f in files:
        content = '%s/%s' % (path, f)
        ctx[f.split('.')[0]] = content
    return render(request, 'pages/'+ sub_path + '.html', ctx)
