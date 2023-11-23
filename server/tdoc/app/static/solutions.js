document.addEventListener('DOMContentLoaded', (event) => {
  // Add buttons to all solution sections.
  document.querySelectorAll('div.response').forEach((el) => {
    // Add a button before each solution section. The button toggles the
    // visibility of the section.
    const btn = document.createElement("button");
    btn.className = "solution";
    btn.textContent = "Solution";
    btn.addEventListener("click", function () {
      el.classList.toggle("hide");
    });
    el.before(btn);
  });
});
