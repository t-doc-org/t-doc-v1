from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("render-latex", views.renderlatex, name="renderlatex"),
    # path("defaults", views.defaults, name="defaults"),
    # path("submit", views.submit, name="submit"),
]
