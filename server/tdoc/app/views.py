import hashlib
import html
import mimetypes
import os
import pathlib
import re
import struct
import subprocess

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


PKG_DIR = pathlib.Path(__file__).resolve().parent
CONFIGS = PKG_DIR / "configs"
LATEX_CFG = CONFIGS / "latex.cfg"
TEXINPUTS = PKG_DIR / "texinputs"


def random_name(base):
    """Generate a random base name for the rendering output."""
    num = struct.unpack("I", os.urandom(4))[0]
    return f"{base}-{num}"


# Match ANSI escape codes.
ansi_re = re.compile(rb"\x1b\[[\x30-\x3f]*[\x20-\x2f]*[\x40-\x7e]")


def remove_ansi_escapes(s):
    """Remove ANSI escape codes from the given string."""
    return ansi_re.sub(b"", s)


def hash_varint(h, value):
    """Hash the varint representation of an integer."""
    while True:
        h.update(b'%c' % ((value & 0x7f) | (0x80 if value > 0x7f else 0)))
        value >>= 7
        if value == 0: break


def generate_key(latex, config, version):
    """Generate a hash key for an input file and the rendering config."""
    m = hashlib.sha256()
    hash_varint(m, len(latex))
    m.update(latex)
    hash_varint(m, len(config))
    m.update(config)
    hash_varint(m, len(version))
    m.update(version)
    return f"latex:{m.hexdigest()}"


class RenderException(Exception):
    """An exception raised when LaTeX rendering fails."""
    def __init__(self, msg, output):
        super().__init__(msg)
        self.output = output


# Match a <link> tag referencing a specific CSS file.
css_re = r"<link [^>]*href=[\"']%s\.css[\"'][^>]*>"


def inline_css_link(doc, name, css):
    """Replace a <link> tag referencing a CSS file with its content."""
    # <link href='output-2687784357.css' rel='stylesheet' type='text/css' />
    return re.sub(css_re % re.escape(name),
                  '<style type="text/css">' + html.escape(css) + "</style>\n",
                  doc)


def doc(request, path):
    """Handle requests to the /doc/ endpoint."""
    doc_path = settings.DOC_ROOT
    for part in path.split("/"):
        doc_path /= part
    if not doc_path.suffix:
        doc_path = doc_path.with_suffix(".tex")
    if doc_path.suffix == ".tex":
        return render_tex(request, doc_path)
    return send_file(request, doc_path)


def render_tex(request, doc_path):
    """Handle the rendering of a LaTeX document."""
    latex = doc_path.read_bytes()
    config = LATEX_CFG.read_bytes()
    version = subprocess.run(["make4ht", "-v"], capture_output=True).stdout
    key = generate_key(latex, config, version)

    def render():
        name = random_name("output")
        try:
            args = ["make4ht", "-j", name, "-x", "-c", LATEX_CFG]
            if settings.RENDER_DRAFT:
                args += ["-m", "draft"]
            args += ["-", "mathjax"]
            env = os.environ.copy()
            env["TEXINPUTS"] = f"{TEXINPUTS}:"
            res = subprocess.run(args, input=latex, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, cwd=settings.TMP,
                                 env=env)
            if res.returncode != 0:
                raise RenderException("failed to render", res.stdout)
            content = (settings.TMP / f"{name}.html").read_text()
            css = (settings.TMP / f"{name}.css").read_text()
            return inline_css_link(content, name, css)
        finally:
            for path in settings.TMP.glob(f"{name}*"):
                path.unlink()

    try:
        htmlresp = cache.get_or_set(key, render)
        return HttpResponse(htmlresp, content_type="text/html")
    except RenderException as e:
        return HttpResponse(remove_ansi_escapes(e.output), status=400,
                            content_type="text/plain")


def send_file(request, doc_path):
    """Send a file directly from the filesystem."""
    content_type = mimetypes.guess_type(doc_path, strict=False)[0]
    try:
        return HttpResponse(doc_path.read_bytes(), content_type=content_type)
    except IOError as e:
        return HttpResponse(str(e), status=400, content_type="text/plain")
