from django.urls import path

from . import views

urlpatterns = [
    path("doc/<file>", views.doc, name="doc"),
]
