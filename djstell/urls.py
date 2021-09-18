from django.contrib import admin
from django.urls import include, path
import debug_toolbar

import djstell.pages.views as dpv

urlpatterns = [
    # Example:
    path('', include('djstell.pages.urls')),

    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),

    path('<path:path>', dpv.last_resort),
]

handler404 = dpv.not_found
