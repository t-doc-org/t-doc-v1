import os

DEBUG = True
SECRET_KEY = 'django-insecure-dy2*ac$z1s9(9s*c4ksu_7mwg1d8kb)r2y#&-57+dy#cvp4q!'

_cache_marker = Path(CACHES['default']['LOCATION']) / 't-doc.marker-658629873'
try:
    _cache_marker.unlink(missing_ok=True)
    _cache_marker.touch()
except PermissionError:
    CACHES['default']['LOCATION'] = BASE_DIR / 'cache'

RENDER_MODE = "draft"
