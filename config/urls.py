from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views

from djangocon_2020.site.views import default_view

urlpatterns = [
	    # Django Admin, use {% url 'admin:index' %}
	    path(settings.ADMIN_URL, admin.site.urls),
	    # User management
	    path("users/", include("djangocon_2020.users.urls", namespace="users")),
	    path("accounts/", include("allauth.urls")),
	    # Your stuff: custom urls includes go here
	    path("", default_view),
        path("<slug:menu>/", default_view),
        path("<slug:menu>/<slug:submenu>/", default_view)
	] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
