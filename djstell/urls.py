from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import debug_toolbar

urlpatterns = [
    # Example:
    url(r'', include('djstell.pages.urls')),

    path('__debug__/', include(debug_toolbar.urls)),

    # Uncomment this for admin:
#     url(r'^admin/', include('django.contrib.admin.urls')),
]

if settings.STATIC_URL:
    urlpatterns += staticfiles_urlpatterns()
