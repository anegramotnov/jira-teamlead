// following https://github.com/mkdocs/mkdocs/issues/2028

document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll("table").forEach(function(table) {
    table.classList.add("docutils");
  });
});
