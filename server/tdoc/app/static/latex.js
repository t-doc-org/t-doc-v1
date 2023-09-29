// MathJax normally operates on whole documents. It doesn't natively know how
// to handle shadow DOMs. The code below hooks into various components to allow
// it to render in shadow DOMs. It is a cleaned-up version of code taken from:
//
// https://github.com/mathjax/MathJax/issues/2162#issuecomment-506962519
// https://github.com/mathjax/MathJax/issues/2195#issuecomment-533840961
// https://github.com/mathjax/MathJax/issues/2590#issuecomment-751398270
window.MathJax = {
  tex: {
    tags: "ams",
    inlineMath: [['$', '$'], ['\\(', '\\)']],
  },
  options: {
    skipHtmlTags: {'[+]': ['tdoc-latex']}
  },
  startup: {
    ready: () => {
      const mathjax = MathJax._.mathjax.mathjax;
      const HTMLAdaptor = MathJax._.adaptors.HTMLAdaptor.HTMLAdaptor;
      const HTMLHandler = MathJax._.handlers.html.HTMLHandler.HTMLHandler;
      const AbstractHandler = MathJax._.core.Handler.AbstractHandler.prototype;
      const startup = MathJax.startup;

      // Extend HTMLAdaptor to handle the shadow DOM as the document.
      class ShadowAdaptor extends HTMLAdaptor {
        create(kind, ns) {
          const doc = (this.document.createElement ? this.document
                       : this.window.document);
          return (ns ? doc.createElementNS(ns, kind) : doc.createElement(kind));
        }

        text(text) {
          const doc = (this.document.createTextNode ? this.document
                       : this.window.document);
          return doc.createTextNode(text);
        }

        head(doc) {
          return doc.head || (doc.firstChild || {}).firstChild || doc;
        }

        body(doc) {
          return doc.body || (doc.firstChild || {}).lastChild || doc;
        }

        root(doc) {
          return doc.documentElement || doc.firstChild || doc;
        }
      }

      // Extend HTMLHandler to handle the shadow DOM as the document.
      class ShadowHandler extends HTMLHandler {
        create(doc, options) {
          const adaptor = this.adaptor;
          if (typeof(doc) === 'string') {
            doc = adaptor.parse(doc, 'text/html');
          } else if ((doc instanceof adaptor.window.HTMLElement ||
                      doc instanceof adaptor.window.DocumentFragment) &&
                     !(doc instanceof window.ShadowRoot)) {
            const child = doc;
            doc = adaptor.parse('', 'text/html');
            adaptor.append(adaptor.body(doc), child);
          }
          // We can't use super.create() here, because it doesn't handle the
          // shadow DOM correctly. So we call HTMLHandler's parent class
          // directly instead.
          return AbstractHandler.create.call(this, doc, options);
        }
      }

      // Register the new handler and adaptor.
      startup.registerConstructor('HTMLHandler', ShadowHandler);
      startup.registerConstructor('browserAdaptor',
                                  () => new ShadowAdaptor(window));

      // Create a new MathDocument from the shadow root with the configured
      // input and output jax, then render the document.
      MathJax.typesetShadow = function (root) {
        const InputJax = startup.getInputJax();
        const OutputJax = startup.getOutputJax();
        const html = mathjax.document(root, {InputJax, OutputJax});
        html.render();
        return html;
      }

      MathJax.typesetShadowPromise = function (root) {
        const InputJax = startup.getInputJax();
        const OutputJax = startup.getOutputJax();
        const html = mathjax.document(root, {InputJax, OutputJax});
        return mathjax.handleRetriesFor(() => html.render());
      }

      // Continue with the usual startup.
      MathJax.startup.defaultReady();
    }
  }
};


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                  cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class LatexComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: 'open'});
    this.observer = new MutationObserver(async (mutation) => {
      this.render();
    });
  }

  async connectedCallback() {
    await this.render();
    this.observer.observe(this, {childList: true, characterData: true,
                                 subtree: true});
  }

  disconnectedCallback() {
    this.observer.disconnect();
  }

  async render() {
    console.log("render");
    const text = this.textContent;
    if (!text) return;

    console.log("performing rendering");
    const response = await fetch('/render-latex', {
      method: 'POST',
      headers: {'X-CSRFToken': getCookie('csrftoken')},
      mode: 'same-origin',
      cache: 'no-cache',
      body: text,
    })
    const html = await response.text()
    console.log("response received");
    MathJax.typesetClear([this.shadowRoot.firstChild]);
    this.shadowRoot.innerHTML = '<mjx-doc><mjx-head></mjx-head><mjx-body>' +
                                html + '</mjx-body></mjx-doc>';
    await MathJax.typesetShadowPromise(this.shadowRoot);
  }
}

customElements.define('tdoc-latex', LatexComponent);
