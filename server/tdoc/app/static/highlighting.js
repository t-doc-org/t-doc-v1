import hljs from 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/es/highlight.min.js';

document.addEventListener('DOMContentLoaded', async (event) => {
    // Add the highlight.js stylesheet.
    const css = document.createElement('link');
    css.rel = 'stylesheet'
    css.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js' +
               '/11.9.0/styles/default.min.css';
    css.async = true;
    document.head.appendChild(css);

    // Add hljs as a global variable, because highlightjs-line-numbers.js
    // patches it on import, and expects it to be there. We need to use a
    // dynamic import to ensure it happens after setting the global.
    window.hljs = hljs;
    await import('https://cdn.jsdelivr.net/npm/highlightjs-line-numbers.js' +
                 '@2.8.0/dist/highlightjs-line-numbers.min.js');

    // Highlight all verbatim sections.
    document.querySelectorAll('pre.verbatim').forEach((el) => {
        // Extract an optional language identifier prefix of the form
        // "{python}".
        const text = el.innerHTML;
        const re = /^\{([a-zA-Z0-9_-]+)\}( *\n)?/;
        const m = re.exec(text);
        if (m) {  // Found, remove the prefix and add the relevant CSS class
            const lang = m[1];
            el.innerHTML = text.substr(m[0].length);
            el.classList.add(`language-${lang}`);
        }
        hljs.highlightElement(el);
        hljs.lineNumbersBlock(el);
    });
});
