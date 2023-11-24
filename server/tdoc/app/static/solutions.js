document.addEventListener('DOMContentLoaded', (event) => {
  // Wrap solution sections.
  let id = 0;
  document.querySelectorAll('div.tdoc-solution').forEach((el) => {
    // Wrap each solution section in a collapsible block. Collapsing is based on
    // a hidden checkbox, triggered by clicking on the label, and CSS selectors
    // that use the "checked" attribute of the checkbox.
    ++id;
    const div = document.createElement("div");
    div.className = "tdoc-solution-wrap";
    div.innerHTML = `
      <input id="tdoc-solution-${id}" class="toggle" type="checkbox">
      <label for="tdoc-solution-${id}">Solution</label>
    `;
    el.replaceWith(div);
    div.appendChild(el);
  });
});
