import hljs from 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/es/highlight.min.js';

document.addEventListener('DOMContentLoaded', (event) => {
    const css = document.createElement("link");
    css.rel = "stylesheet"
    css.href = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css";
    css.async = true;
    document.head.appendChild(css);
    document.querySelectorAll('pre.verbatim').forEach((el) => {
        const text = el.innerHTML;
        const re = /^\{([a-zA-Z0-9_-]+)\}( *\n)?/;
        const m = re.exec(text);
        if (m) {
            const lang = m[1];
            el.innerHTML = text.substr(m[0].length);
            el.classList.add(`language-${lang}`);
            console.log(lang);
        }
        hljs.highlightElement(el);
    });
});
