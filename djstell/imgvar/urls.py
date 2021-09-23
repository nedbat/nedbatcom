from django.urls import path

import djstell.imgvar.views as views

urlpatterns = [
    path('<slug:var>/<path:path>', views.imgvar),
]
