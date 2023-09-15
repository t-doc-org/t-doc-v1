from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

import html
import os
import struct
from subprocess import run

def random_name(base):
    num = struct.unpack("I", os.urandom(4))[0]
    return f"{base}-{num}"

@ensure_csrf_cookie
def index(request):
    return render(request, 'testWebComponent.html')

def renderlatex(request):
    # Command: $ cat testXelatex.tex | make4ht -j latexrendering -
    # Command: $ cat testXelatex.tex | make4ht -d tmp -j latexrendering - mathjax
    # Command: $ cat testXelatexWithcfg.tex | make4ht -c latex.cfg -d tmp -j latexrendering - mathjax
    name = random_name("output")
    latex = request.read()
    print(latex)
    run(["make4ht", "-j", name, "-c", "latex.cfg", "-", "mathjax"], input=latex, check=True)
    try:
        with open(f"{name}.html") as f:
            content = f.read()
        with open(f"{name}.css") as f:
            css = f.read()
        css = '<style type="text/css">' + html.escape(css) + "</style>\n"
        # print(css)
        # print(html)
        return HttpResponse(css + content, content_type="text/html")
    finally:
        run(["make4ht", "-j", name, "-m", "clean", "-"], input="")
        pass
