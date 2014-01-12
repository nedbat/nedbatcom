from django.conf.urls import patterns, include

urlpatterns = patterns('',
    # Example:
    (r'', include('djstell.pages.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
