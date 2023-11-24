import contextlib
import hashlib
import html
import mimetypes
import os
import pathlib
import re
import subprocess
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


PKG_DIR = pathlib.Path(__file__).resolve().parent
CONFIGS = PKG_DIR / "configs"
LATEX_CFG = CONFIGS / "latex.cfg"
TEXINPUTS = PKG_DIR / "texinputs"


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


def generate_key(prefix, /, **kwargs):
    """Generate a hash key for a set of key / value pairs."""
    m = hashlib.sha256()
    for k, v in sorted(kwargs.items()):
        if isinstance(k, str): k = k.encode('utf-8')
        hash_varint(m, len(k))
        m.update(k)
        if isinstance(v, str): v = v.encode('utf-8')
        hash_varint(m, len(v))
        m.update(v)
    return f"{prefix}:{m.hexdigest()}"


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
        return render_latex(request, doc_path)
    return send_file(request, doc_path)


def render_latex(request, doc_path):
    """Handle the rendering of a LaTeX document."""
    latex = doc_path.read_bytes()
    config = LATEX_CFG.read_bytes()
    mode = ("" if "final" in request.GET else "draft" if "draft" in request.GET
            else settings.RENDER_MODE)
    key = generate_key("latex", seed=settings.CACHE_HASH_SEED, latex=latex,
                       config=config, mode=mode)

    def render():
        with output_directory(doc_path) as output:
            args = ["make4ht", "--xetex", "--config", LATEX_CFG,
                    "--jobname", "output"]
            if mode: args += ["-m", mode]
            args += ["-", "mathjax"]
            env = os.environ.copy()
            env["TEXINPUTS"] = f"{TEXINPUTS}:"
            res = subprocess.run(args, input=latex, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, cwd=output,
                                 env=env)
            if res.returncode != 0:
                raise RenderException("failed to render", res.stdout)
            content = (output / "output.html").read_text()
            css = (output / "output.css").read_text()
            return inline_css_link(content, "output", css)

    try:
        htmlresp = cache.get_or_set(key, render)
        return HttpResponse(htmlresp, content_type="text/html")
    except RenderException as e:
        return HttpResponse(remove_ansi_escapes(e.output), status=400,
                            content_type="text/plain")


@contextlib.contextmanager
def output_directory(doc_path):
    """Create an output directory for LaTeX rendering.

    make4ht resolves relative paths in the input file relative to the current
    working directory, not the input file. But we don't want to set the CWD to
    the directory containing the input file, because make4ht writes to it.

    So instead, we create a temporary directory, set it as CWD, and create
    symlinks to all the sub-directories that exist next to the input files.
    """
    with tempfile.TemporaryDirectory(prefix="tdoc-") as name:
        output = pathlib.Path(name)
        for p in doc_path.parent.iterdir():
            if p.is_dir():
                (output / p.name).symlink_to(p, target_is_directory=True)
        yield output


def send_file(request, doc_path):
    """Send a file directly from the filesystem."""
    content_type = mimetypes.guess_type(doc_path, strict=False)[0]
    try:
        return HttpResponse(doc_path.read_bytes(), content_type=content_type)
    except IOError as e:
        return HttpResponse(str(e), status=400, content_type="text/plain")
