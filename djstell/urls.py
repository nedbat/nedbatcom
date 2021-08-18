from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Example:
    url(r'', include('djstell.pages.urls')),

    # Uncomment this for admin:
#     url(r'^admin/', include('django.contrib.admin.urls')),
]

if settings.STATIC_URL:
    urlpatterns += staticfiles_urlpatterns()
