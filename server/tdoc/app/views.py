from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def renderlatex(request):
    # Command: $ cat testXelatexWithcfg.tex | make4ht -c latex.cfg -d tmp -j latexrendering - mathjax
    name = random_name("output")
    latex = request.read()
    try:
        res = subprocess.run(
            ["make4ht", "-j", name, "-c", "latex.cfg", "-", "mathjax"],
            input=latex, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if res.returncode != 0:
            response = HttpResponse(ansiRE.sub(b"", res.stdout), status=400, content_type="text/plain")
            return response

        with open(f"{name}.html") as f:
            content = f.read()
        with open(f"{name}.css") as f:
            css = f.read()
        css = '<style type="text/css">' + html.escape(css) + "</style>\n"
        return HttpResponse(css + content, content_type="text/html")
    finally:
        subprocess.run(["make4ht", "-j", name, "-m", "clean", "-"], input="")
