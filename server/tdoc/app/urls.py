from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("defaults", views.defaults, name="defaults"),
    # path("submit", views.submit, name="submit"),
]
