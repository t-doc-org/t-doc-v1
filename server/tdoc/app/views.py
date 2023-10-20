from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import hashlib
import html
import os
import re
import struct
import subprocess

def random_name(base):
    num = struct.unpack("I", os.urandom(4))[0]
    return f"{base}-{num}"

#use to delete ANSI escape code in error message
ansiRE = re.compile(rb"\x1b\[[\x30-\x3f]*[\x20-\x2f]*[\x40-\x7e]")

def hash_varint(m, value):
    while True:
        m.update(b'%c' % ((value & 0x7f) | (0x80 if value > 0x7f else 0)))
        value >>= 7
        if value == 0: break

def generate_key(latex, config, version):
    m = hashlib.sha256()
    hash_varint(m, len(latex))
    m.update(latex)
    hash_varint(m, len(config))
    m.update(config)
    hash_varint(m, len(version))
    m.update(version)
    return f"latex:{m.hexdigest()}"

class RenderException(Exception):
    def __init__(self, msg, output):
        super().__init__(msg)
        self.output = output


css_re = r"<link [^>]*href=[\"']%s\.css[\"'][^>]*>"

def doc(request, file):
    name = random_name("output")
    with open(settings.TEX_ROOT / f"{file}.tex", "rb") as f:
        latex = f.read()
    configpath = settings.TEX_ROOT / "latex.cfg"
    with open(configpath, "rb") as f:
        config = f.read()
    version = subprocess.run(["make4ht", "-v"], capture_output=True).stdout
    key = generate_key(latex, config, version)

    def render():
        try:
            res = subprocess.run(
                ["make4ht", "-j", name, "-c", configpath, "-", "mathjax"],
                input=latex, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=settings.TMP)
            if res.returncode != 0:
                raise RenderException("failed to render", res.stdout)
            with open(settings.TMP / f"{name}.css") as f:
                css = f.read()
            with open(settings.TMP / f"{name}.html") as f:
                content = f.read()
                # <link href='output-2687784357.css' rel='stylesheet' type='text/css' />
                content = re.sub(css_re % re.escape(name), '<style type="text/css">' + html.escape(css) + "</style>\n", content)
            return content
        finally:
            for path in settings.TMP.glob(f"{name}*"):
                path.unlink()

    try:
        htmlresp = cache.get_or_set(key, render)
        return HttpResponse(htmlresp, content_type="text/html")
    except RenderException as e:
        return HttpResponse(ansiRE.sub(b"", e.output), status=400, content_type="text/plain")

