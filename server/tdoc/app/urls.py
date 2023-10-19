from django.urls import path

from . import views

urlpatterns = [
    path("render-html/<file>", views.renderhtml, name="renderhtml"),
    # path("render-latex", views.renderlatex, name="renderlatex"),
]
