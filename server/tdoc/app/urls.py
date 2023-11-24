from django.urls import path, register_converter
from django.urls.converters import StringConverter

from . import views


class SafePathConverter(StringConverter):
    """A URL converter that accepts safe filesystem paths.

    It matches relative URL paths where each component doesn't start with a "."
    and contains no backslashes. This prevents filesystem traversal with "." and
    ".." components, and hides common directories that aren't supposed to be
    exposed, e.g. ".hg".
    """
    regex = r"(?:[^./\\][^/\\]*/?)+"


register_converter(SafePathConverter, "safepath")


urlpatterns = [
    path("doc/<safepath:path>", views.doc, name="doc"),
]
