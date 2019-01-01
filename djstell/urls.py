from django.conf.urls import include, url

urlpatterns = [
    # Example:
    url(r'', include('djstell.pages.urls')),

    # Uncomment this for admin:
#     url(r'^admin/', include('django.contrib.admin.urls')),
]
