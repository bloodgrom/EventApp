// add event listeners for the add and remove specialization buttons
document.getElementById("add-specialization").addEventListener("click", addSpecialization);
document.getElementById("specialization-container").addEventListener("click", removeSpecialization);

// add a new specialization text field
function addSpecialization() {
  // create the new specialization text field
  const newSpecialization = document.createElement("div");
  newSpecialization.innerHTML = `
    <input type="text" name="specialization[]" required>
    <button type="button" class="remove-specialization">X</button>
  `;
  
  // append the new specialization text field to the specialization container
  document.getElementById("specialization-container").appendChild(newSpecialization);
  
  // check if there are two or more specialization text fields
  if (document.getElementById("specialization-container").children.length >= 2) {
    // add the remove button to the first specialization text field if it doesn't already have one
    const firstSpecialization = document.getElementById("specialization-container").firstElementChild;
    if (!firstSpecialization.lastElementChild.classList.contains("remove-specialization")) {
      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.classList.add("remove-specialization");
      removeButton.textContent = "X";
      firstSpecialization.appendChild(removeButton);
    }
  }
}



// remove a specialization text field
function removeSpecialization(e) {
  // check if the target element is the remove specialization button
  if (e.target.classList.contains("remove-specialization")) {
    // check if there is only one specialization text field
    if (document.getElementById("specialization-container").children.length == 1) {
      // display an alert message
      alert("There must be at least one specialization.");
    } else {
      // remove the parent element of the remove specialization button (the specialization text field)
      e.target.parentElement.remove();
      
      // check if there is only one specialization text field
      if (document.getElementById("specialization-container").children.length == 1) {
        // remove the remove button from the first specialization text field
        const firstSpecialization = document.getElementById("specialization-container").firstElementChild;
        firstSpecialization.removeChild(firstSpecialization.lastElementChild);
      }
    }
  }
}
