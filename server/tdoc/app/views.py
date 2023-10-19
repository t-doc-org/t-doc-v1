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

# @csrf_exempt
# def renderlatex(request):
#     name = random_name("output")
#     latex = request.read()
#     with open("latex.cfg") as f:
#         config = f.read()
#     version = subprocess.run(["make4ht", "-v"], capture_output=True).stdout
#     key = generate_key(latex, config, version)

#     def render():
#         try:
#             res = subprocess.run(
#                 ["make4ht", "-j", name, "-c", "latex.cfg", "-", "mathjax"],
#                 input=latex, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#             if res.returncode != 0:
#                 raise RenderException("failed to render", res.stdout)
#             with open(f"{name}.html") as f:
#                 content = f.read()
#             with open(f"{name}.css") as f:
#                 css = f.read()
#             return '<style type="text/css">' + html.escape(css) + "</style>\n" + content
#         finally:
#             subprocess.run(["make4ht", "-j", name, "-m", "clean", "-"], input="")

#     try:
#         htmlresp = cache.get_or_set(key, render)
#         return HttpResponse(htmlresp, content_type="text/html")
#     except RenderException as e:
#         return HttpResponse(ansiRE.sub(b"", e.output), status=400, content_type="text/plain")


def renderhtml(request, file):
    name = random_name("output")
    with open(f"{settings.TEX_ROOT}/{file}.tex", "rb") as f:
        latex = f.read()
    configpath = f"{settings.TEX_ROOT}/latex.cfg"
    with open(configpath, "rb") as f:
        config = f.read()
    version = subprocess.run(["make4ht", "-v"], capture_output=True).stdout
    key = generate_key(latex, config, version)

    def render():
        try:
            res = subprocess.run(
                ["make4ht", "-j", name, "-c", configpath, "-", "mathjax"],
                input=latex, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if res.returncode != 0:
                raise RenderException("failed to render", res.stdout)
            with open(f"{name}.html") as f:
                content = f.read()
            with open(f"{name}.css") as f:
                css = f.read()
            return '<style type="text/css">' + html.escape(css) + "</style>\n" + content
        finally:
            subprocess.run(["make4ht", "-j", name, "-m", "clean", "-"], input="")

    try:
        htmlresp = cache.get_or_set(key, render)
        return HttpResponse(htmlresp, content_type="text/html")
    except RenderException as e:
        return HttpResponse(ansiRE.sub(b"", e.output), status=400, content_type="text/plain")

