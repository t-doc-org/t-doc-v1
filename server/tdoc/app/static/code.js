import hljs from 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/es/highlight.min.js';

function builtinRead(x) {
    if (Sk.builtinFiles === undefined ||
        Sk.builtinFiles["files"][x] === undefined)
            throw "File not found: '" + x + "'";
    return Sk.builtinFiles["files"][x];
}

document.addEventListener('DOMContentLoaded', async (event) => {
    // Add the highlight.js stylesheet.
    const css = document.createElement('link');
    css.rel = 'stylesheet'
    css.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js' +
               '/11.9.0/styles/stackoverflow-light.min.css';
    css.async = true;
    document.head.appendChild(css);

    // Add hljs as a global variable, because highlightjs-line-numbers.js
    // patches it on import, and expects it to be there. We need to use a
    // dynamic import to ensure it happens after setting the global.
    window.hljs = hljs;
    await import('https://cdn.jsdelivr.net/npm/highlightjs-line-numbers.js' +
                 '@2.8.0/dist/highlightjs-line-numbers.min.js');

    // Load Skulpt.
    const skulpt = document.createElement('script');
    skulpt.src = 'https://skulpt.org/js/skulpt.min.js';
    skulpt.type = 'text/javascript';
    document.head.appendChild(skulpt);
    // Because the standard library depends on Skulpt,
    // we wait until Skulpt loaded
    skulpt.addEventListener('load', () => {
        const skulpt_stdlib = document.createElement('script');
        skulpt_stdlib.src = 'https://skulpt.org/js/skulpt-stdlib.js';
        skulpt_stdlib.type = 'text/javascript';
        document.head.appendChild(skulpt_stdlib);
    });

    // Manage code (display or add possibility to execute) and highlight all
    // code sections.
    document.querySelectorAll('div.tdoc-code > span').forEach((el) => {
        // Determine the code language and any options.
        let lang, interactive = false, turtle = false;
        el.parentNode.classList.forEach((c) => {
            if (c.startsWith("tdoc-lang-")) lang = c.substring(10);
            if (c.startsWith("tdoc-code-")) {
                if (c.includes("interactive")) interactive = true;
                if (c.includes("turtle")) turtle = true;
            }
        });

        // Remove leading spaces that are sometimes added by LaTeX.
        const code = el.innerHTML.replaceAll(' ', ''); // à corriger
        el.innerHTML = code;
        el.classList.add(`language-${lang}`);  // Set class for hljs

        // Add a button to execute code.
        if (lang == "python" && interactive) {
            // Convert code in HTML to text.
            const code_text = code.replaceAll('&nbsp;', ' ')
                                  .replaceAll('&lt;', '<')
                                  .replaceAll('&gt;', '>')
                                  .replaceAll('&amp;', '&');
            const button = document.createElement("button");
            button.innerHTML = "Exécuter";
            el.after(button);

            // Add a pre to display the result.
            let pre, turtleDiv;
            button.addEventListener('click', async (event) => {
                // Code execution
                if (button.innerHTML == "Exécuter") {
                    button.innerHTML = "Effacer";
                    if (turtle) {
                        turtleDiv = document.createElement("div");
                        turtleDiv.className = "tdoc-turtle";
                        button.after(turtleDiv);
                        Sk.TurtleGraphics = {target: turtleDiv};
                        Sk.TurtleGraphics.width = 800;
                        Sk.TurtleGraphics.height = 500;
                    }

                    Sk.configure({
                        inputfun: (prompt) => window.prompt(prompt),
                        inputfunTakesPrompt: true,
                        output: (text) => {
                            if (!pre && text != "") {
                                pre = document.createElement("pre");
                                pre.className = "tdoc-execution";
                                button.after(pre);
                            }
                            pre.innerHTML += text;
                        },
                        read: builtinRead
                    });
                    await Sk.misceval.asyncToPromise(() => {
                        return Sk.importMainWithBody("<stdin>", false,
                                                     code_text, true);
                   });
                } else {  // Clear
                    button.innerHTML = "Exécuter";
                    if (pre) {
                        pre.remove();
                        pre = undefined;
                    }
                    if (turtleDiv) {
                        turtleDiv.remove();
                        turtleDiv = undefined;
                    }
                }
            });
        }
        hljs.highlightElement(el);
        hljs.lineNumbersBlock(el);
    });
});
