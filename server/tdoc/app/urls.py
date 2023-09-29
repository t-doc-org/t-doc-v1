from django.urls import path

from . import views

urlpatterns = [
    path("render-latex", views.renderlatex, name="renderlatex"),
]
