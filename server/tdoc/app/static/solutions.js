document.addEventListener('DOMContentLoaded', (event) => {
  console.log("Load");

  document.querySelectorAll('div.response').forEach((el) => {
    console.log("each");
    const btn = document.createElement("button");
    btn.className = "solution";
    btn.textContent = "Solution";
    el.before(btn);

    const clickBtn = function () {
      console.log("onclick");
       el.classList.toggle("hide");
    };

    btn.addEventListener("click", clickBtn);

  });

});

