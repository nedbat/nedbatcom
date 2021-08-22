from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import debug_toolbar

urlpatterns = [
    # Example:
    path('', include('djstell.pages.urls')),

    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.STATIC_URL:
    urlpatterns += staticfiles_urlpatterns()
