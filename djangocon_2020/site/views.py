from django.shortcuts import render
from os import walk

from config.settings.base import APPS_DIR


def default_view(request, menu='home', submenu=None):
    path = APPS_DIR.__str__() + '/content/' + menu + ('/' + submenu if submenu else '')
    ctx = {}
    files = []
    for dirpath, dirname, filenames in walk(path):
        files.extend(filenames)
        break
    ctx['files'] = []
    for f in sorted(files):
        content = '%s/%s' % (path, f)
        ctx['files'].append(content)
    print(ctx['files'])
    print('pages/' + (menu if menu == 'home' else 'default') + '.html')
    return render(request, 'pages/' + (menu if menu == 'home' else 'default') + '.html', ctx)
