from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.urls import re_path
from django.views.static import serve as serve_static
import debug_toolbar

urlpatterns = [
    # Example:
    path('', include('djstell.pages.urls')),

    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.STATIC_URL:
    urlpatterns += [
        # NOTE: this is a hack, it's a copy of what staticfiles_urlpatterns
        # would give me if it didn't examine settings.DEBUG.
        re_path(r'^(?P<path>.*)$', serve_static, kwargs={'document_root': ''}),
    ]
