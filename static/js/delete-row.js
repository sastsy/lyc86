let procRows = table.querySelectorAll("tbody tr");
for (let i = 0; i < procRows.length; i++) {
  procRows[i].innerHTML += '<td><button  title="Remove"></td>';
}

zen.querySelector("tbody").addEventListener("click", function(e) {
 if (e.target.nodeName == "BUTTON") {
 let cell = e.target.parentNode;
 cell.parentNode.classList.add("hidden");
 e.target.remove();
 }
})