document.addEventListener('DOMContentLoaded', (event) => {
  // Add buttons to all solution sections.
  document.querySelectorAll('div.tdoc-answer').forEach((el) => {
    // Add a button before each solution section. The button toggles the
    // visibility of the section.
    const btn = document.createElement("button");
    btn.className = "tdoc-solution";
    btn.textContent = "Solution";
    btn.addEventListener("click", function () {
      el.classList.toggle("tdoc-hidden");
    });
    el.before(btn);
  });
});
