const table = document.getElementById("user-table");
const selectedRowData = document.getElementById("selected-row-data");
const username = document.getElementById("username");
const email = document.getElementById("email");
const role = document.getElementById("role");
const change_button = document.getElementById("change_button");

let lastSelectedRow;

table.addEventListener("click", (event) => {
  if (event.target.tagName === "TD") {
    const selectedRow = event.target.parentNode;
    if (selectedRow.parentNode.nodeName === 'THEAD') {
      return;
    }
    if (lastSelectedRow) {
      lastSelectedRow.classList.remove("selected");
    }
    selectedRow.classList.add("selected");
    lastSelectedRow = selectedRow;
    const cells = selectedRow.getElementsByTagName("td");
    // let data = "";
    // for (let i = 0; i < cells.length; i++) {
    //   data += cells[i].textContent + " ";
    // }
    // selectedRowData.textContent = data;

    username.textContent = cells[0].textContent;
    email.textContent = cells[1].textContent;
    role.textContent = cells[2].textContent;

    var django_param = "?user=" + username.textContent
    var url_suffix = "location.href='"
    var url_prefix = "';"
    var full_url = url_suffix + url_django + django_param + url_prefix

    change_button.setAttribute('onclick', full_url);
  }
});
